# -*- coding: utf-8 -*-
# pylint: disable=attribute-defined-outside-init, invalid-name, objects-update-used

import base64

from modernrpc.exceptions import RPC_INTERNAL_ERROR
from parameterized import parameterized

from tcms.rpc.tests.utils import APITestCase
from tcms.xmlrpc_wrapper import XmlRPCFault


class TestValidators(APITestCase):
    @parameterized.expand(
        [
            "inline_javascript.svg",
            "inline_javascript_mixed_case.svg",
            "inline_javascript_3mb.svg",
        ]
    )
    def test_uploading_svg_with_inline_script_should_fail(self, file_name):
        with open(f"tests/ui/data/{file_name}", "rb") as svg_file:
            b64 = base64.b64encode(svg_file.read()).decode()

            with self.assertRaises(XmlRPCFault) as ctx:
                self.rpc_client.User.add_attachment("inline_javascript.svg", b64)

            self.assertEqual(ctx.exception.faultCode, RPC_INTERNAL_ERROR)

    @parameterized.expand(
        [
            "svg_with_onload_attribute_01.svg",
            "svg_with_onload_attribute_02.svg",
            "svg_with_onload_attribute_03.svg",
        ]
    )
    def test_uploading_svg_with_forbidden_attributes_should_fail(self, file_name):
        with open(f"tests/ui/data/{file_name}", "rb") as svg_file:
            b64 = base64.b64encode(svg_file.read()).decode()

            with self.assertRaises(XmlRPCFault) as ctx:
                self.rpc_client.User.add_attachment("image.svg", b64)

            self.assertEqual(ctx.exception.faultCode, RPC_INTERNAL_ERROR)

    def test_uploading_filename_ending_in_dot_exe_should_fail(self):
        with self.assertRaises(XmlRPCFault) as ctx:
            self.rpc_client.User.add_attachment("hello.exe", "a2l3aXRjbXM=")

        self.assertEqual(ctx.exception.faultCode, RPC_INTERNAL_ERROR)

    def test_uploading_real_exe_file_should_fail(self):
        with open("tests/ui/data/reactos_csrss.exe", "rb") as exe_file:
            b64 = base64.b64encode(exe_file.read()).decode()

            with self.assertRaises(XmlRPCFault) as ctx:
                self.rpc_client.User.add_attachment("csrss.exe_from_reactos", b64)

            self.assertEqual(ctx.exception.faultCode, RPC_INTERNAL_ERROR)

    def test_uploading_txt_file_should_pass(self):
        with open("tests/ui/data/change-report.txt", "rb") as txt_file:
            b64 = base64.b64encode(txt_file.read()).decode()

            self.rpc_client.User.add_attachment("change-report.txt", b64)
