import { jsonRPC } from './jsonrpc'
import { unescapeHTML } from './utils'

/*
    Override markdown rendering defaults for Simple MDE.

    This resolves XSS vulnerability which can be exploited
    when previewing malicious text in the editor.

    https://github.com/sparksuite/simplemde-markdown-editor/issues/721
    https://snyk.io/vuln/SNYK-JS-SIMPLEMDE-72570
*/
SimpleMDE.prototype.markdown = function (text) {
    alert('RuntimeError - markdown rendering is now backend side')
}

/*
    SimpleMDE binds Tab and Shift-Tab to indenting, so a keyboard could not leave
    the editor. They still indent and unindent a list item; anywhere else the
    browser moves the focus, as it does from a plain text area.
*/
function tabLeavesTheEditor (cm) {
    const CodeMirror = cm.constructor
    // false: CodeMirror leaves the key to the browser
    CodeMirror.keyMap.tabLeavesTheEditor = { Tab: false, 'Shift-Tab': false, fallthrough: 'default' }

    // SimpleMDE's mode is an overlay over GitHub-flavoured Markdown, so the list
    // state is the innermost mode's
    const inList = () => {
        const state = cm.getStateAfter(cm.listSelections()[0].head.line)
        return Boolean(CodeMirror.innerMode(cm.getMode(), state).state.list)
    }
    cm.setOption('extraKeys', Object.assign({}, cm.getOption('extraKeys'), {
        Tab: () => inList() ? cm.execCommand('indentMore') : CodeMirror.Pass,
        'Shift-Tab': () => inList() ? cm.execCommand('indentLess') : CodeMirror.Pass
    }))
    cm.setOption('keyMap', 'tabLeavesTheEditor')
}

/*
    textArea - a DOM element, not jQuery one, of a text area
    fileUpload - a jQuery element of a hidden file upload field
    autoSaveId - unique ID for autosave!
*/
export function initSimpleMDE (textArea, fileUploadElement, autoSaveId = window.location.toString()) {
    if (!textArea || !fileUploadElement) {
        return null
    }

    const simpleMDE = new SimpleMDE({
        element: textArea,
        autoDownloadFontAwesome: false,
        renderingConfig: {
            codeSyntaxHighlighting: true
        },
        toolbar: [
            'heading', 'bold', 'italic', 'strikethrough', '|',
            'ordered-list', 'unordered-list', 'table', 'horizontal-rule', 'code', 'quote', '|',
            'link',
            {
                // todo: standard shortcut is (Ctrl-Alt-I) but I can't find a way
                // to assign shortcuts to customized buttons
                name: 'image',
                action: () => {
                    fileUploadElement.click()
                },
                className: 'fa fa-picture-o',
                title: 'Insert Image'
            },
            {
                name: 'file',
                action: () => {
                    fileUploadElement.click()
                },
                className: 'fa fa-paperclip',
                title: 'Attach File'
            },
            '|', 'preview', 'side-by-side', 'fullscreen', '|', 'guide'
        ],
        autosave: {
            enabled: true,
            uniqueId: autoSaveId,
            delay: 5000
        },
        tabSize: 4,
        indentWithTabs: false,
        previewRender: function (plainText) {
            let renderedText

            jsonRPC('Markdown.render', plainText, function (result) {
                renderedText = unescapeHTML(result)
            }, true)

            return renderedText
        }
    })

    tabLeavesTheEditor(simpleMDE.codemirror)

    fileUploadElement.change(function () {
        const attachment = this.files[0]
        const reader = new FileReader()

        reader.onload = e => {
            const dataUri = e.target.result
            const mimeType = dataUri.split(':')[1]
            const b64content = dataUri.split('base64,')[1]

            jsonRPC('User.add_attachment', [attachment.name, b64content], data => {
                const cm = simpleMDE.codemirror
                const endPoint = cm.getCursor('end')
                let text = `[${data.filename}](${data.url})\n`

                if (mimeType.startsWith('image')) {
                    text = '!' + text
                }

                cm.replaceSelection(text)
                endPoint.ch += text.length
                cm.setSelection(endPoint, endPoint)
                cm.focus()
            })
        }
        reader.readAsDataURL(attachment)
    })

    return simpleMDE
}
