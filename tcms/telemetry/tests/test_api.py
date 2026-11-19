# -*- coding: utf-8 -*-

from parameterized import parameterized

from tcms.testruns.models import TestExecutionStatus
from tcms.tests import LoggedInTestCase
from tcms.tests.factories import TestCaseFactory, TestExecutionFactory, TestRunFactory


class StatusMatrix(LoggedInTestCase):
    """Test Testing.status_matrix"""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.test_run = TestRunFactory()
        cls.test_case = TestCaseFactory()

    @parameterized.expand(
        [
            ("PASSED", "FAILED", "FAILED"),
            ("FAILED", "PASSED", "FAILED"),
            ("PASSED", "IDLE", "IDLE"),
            ("BLOCKED", "IDLE", "BLOCKED"),
        ]
    )
    def test_shows_worst_status_when_case_executed_more_than_once_in_run(
        self, first_status, second_status, expected_status
    ):
        executions = {}
        for status_name in (first_status, second_status):
            executions[status_name] = TestExecutionFactory(
                run=self.test_run,
                case=self.test_case,
                build=self.test_run.build,
                status=TestExecutionStatus.objects.get(name=status_name),
            )

        # the Execution Matrix page calls this method via JSON-RPC
        response = self.client.post(
            "/json-rpc/",
            {
                "id": "jsonrpc",
                "jsonrpc": "2.0",
                "method": "Testing.status_matrix",
                "params": [{"run": self.test_run.pk}],
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        result = response.json()["result"]
        shown = result["executions"][f"{self.test_case.pk}-{self.test_run.pk}"]
        self.assertEqual(shown["pk"], executions[expected_status].pk)
        self.assertEqual(shown["status_id"], executions[expected_status].status_id)
