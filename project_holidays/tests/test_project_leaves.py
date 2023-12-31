# -*- encoding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import datetime

from odoo.addons.mail.tests.common import mail_new_test_user
from odoo.tests import common


class TestProjectLeaves(common.TransactionCase):

    def setUp(self):
        super().setUp()

        self.user_hruser = mail_new_test_user(self.env, login='usertest', groups='base.group_user,hr_holidays.group_hr_holidays_user')
        self.employee_hruser = self.env['hr.employee'].create({
            'name': 'Test HrUser',
            'user_id': self.user_hruser.id,
            'tz': 'UTC',
        })

        self.leave_type = self.env['hr.leave.type'].create({
            'name': 'time off',
            'requires_allocation': 'no',
            'request_unit': 'hour',
        })

    def test_simple_employee_leave(self):

        leave = self.env['hr.leave'].sudo().create({
            'holiday_status_id': self.leave_type.id,
            'employee_id': self.employee_hruser.id,
            'date_from': datetime.datetime(2020, 1, 1, 8, 0),
            'date_to': datetime.datetime(2020, 1, 1, 17, 0),
        })

        task_1 = self.env['project.task'].create({
            'name': "Task 1",
            'user_ids': self.user_hruser,
            'planned_date_begin': datetime.datetime(2020, 1, 1, 8, 0),
            'planned_date_end': datetime.datetime(2020, 1, 1, 17, 0),
        })
        task_2 = self.env['project.task'].create({
            'name': "Task 2",
            'user_ids': self.user_hruser,
            'planned_date_begin': datetime.datetime(2020, 1, 2, 8, 0),
            'planned_date_end': datetime.datetime(2020, 1, 2, 17, 0),
        })

        self.assertNotEqual(task_1.with_context(include_past=True).leave_warning, False,
                            "leave is not validated , but warning for requested time off")

        leave.action_validate()

        self.assertNotEqual(task_1.with_context(include_past=True).leave_warning, False,
                            "employee is on leave, should have a warning")
        self.assertNotEqual(task_1.with_context(include_past=True).leave_warning.startswith(
            "Test HrUser is on time off on that day"), "single day task, should show date")

        self.assertEqual(task_2.with_context(include_past=True).leave_warning, False,
                         "employee is not on leave, no warning")

    def test_multiple_leaves(self):
        self.env['hr.leave'].sudo().create({
            'holiday_status_id': self.leave_type.id,
            'employee_id': self.employee_hruser.id,
            'date_from': datetime.datetime(2020, 1, 6, 8, 0),
            'date_to': datetime.datetime(2020, 1, 7, 17, 0),
        }).action_validate()

        self.env['hr.leave'].sudo().create({
            'holiday_status_id': self.leave_type.id,
            'employee_id': self.employee_hruser.id,
            'date_from': datetime.datetime(2020, 1, 8, 8, 0),
            'date_to': datetime.datetime(2020, 1, 10, 17, 0),
        }).action_validate()

        task_1 = self.env['project.task'].create({
            'name': "Task 1",
            'user_ids': self.user_hruser,
            'planned_date_begin': datetime.datetime(2020, 1, 6, 8, 0),
            'planned_date_end': datetime.datetime(2020, 1, 6, 17, 0),
        })

        self.assertNotEqual(task_1.with_context(include_past=True).leave_warning, False,
                            "employee is on leave, should have a warning")
        self.assertTrue(task_1.leave_warning.startswith(
            "Test HrUser is on time off from the 01/06/2020 to the 01/07/2020. \n"), "single day task, should show date")

        task_2 = self.env['project.task'].create({
            'name': "Task 2",
            'user_ids': self.user_hruser,
            'planned_date_begin': datetime.datetime(2020, 1, 6, 8, 0),
            'planned_date_end': datetime.datetime(2020, 1, 7, 17, 0),
        })
        self.assertEqual(task_2.with_context(include_past=True).leave_warning,
                         "Test HrUser is on time off from the 01/06/2020 to the 01/07/2020. \n")

        task_3 = self.env['project.task'].create({
            'name': "Task 3",
            'user_ids': self.user_hruser,
            'planned_date_begin': datetime.datetime(2020, 1, 6, 8, 0),
            'planned_date_end': datetime.datetime(2020, 1, 10, 17, 0),
        })
        self.assertEqual(task_3.with_context(include_past=True).leave_warning, "Test HrUser is on time off from the 01/06/2020 to the 01/10/2020. \n",
                         "should show the start of the 1st leave and end of the 2nd")

        #Test leave overlapping a public holiday
        self.env['resource.calendar.leaves'].sudo().create({
            'name':"public holiday",
            "date_from":datetime.datetime(2021, 9, 6, 8, 0),
            'date_to': datetime.datetime(2021, 9, 6, 17, 0),
            "calendar_id":False})

        self.env['hr.leave'].sudo().create({
            'holiday_status_id': self.leave_type.id,
            'employee_id': self.employee_hruser.id,
            'date_from': datetime.datetime(2021, 9, 2, 8, 0),
            'date_to': datetime.datetime(2021, 9, 8, 17, 0),
        }).action_validate()

        task_4 = self.env['project.task'].create({
            'name': "Task 1",
            'user_ids': self.user_hruser,
            'planned_date_begin': datetime.datetime(2021, 9, 1, 8, 0),
            'planned_date_end': datetime.datetime(2021, 9, 30, 17, 0),
        })
        self.assertEqual(task_4.with_context(include_past=True).leave_warning, "Test HrUser is on time off from the 09/02/2021 to the 09/08/2021. \n",
                         "public holiday that are overlapped by a leave should not appear in warning")
