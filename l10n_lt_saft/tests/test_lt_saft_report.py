# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from freezegun import freeze_time

from odoo import Command, fields, tools
from odoo.addons.account_reports.tests.common import TestAccountReportsCommon
from odoo.tests import tagged


@tagged('post_install_l10n', 'post_install', '-at_install')
class TestLtSaftReport(TestAccountReportsCommon):

    @classmethod
    def setUpClass(cls, chart_template_ref='l10n_lt.account_chart_template_lithuania'):
        super().setUpClass(chart_template_ref=chart_template_ref)

        (cls.partner_a + cls.partner_b).write({
            'city': 'Garnich',
            'zip': 'L-8353',
            'country_id': cls.env.ref('base.lu').id,
            'phone': '+352 24 11 11 11',
        })

        cls.company_data['company'].write({
            'city': 'Vilnius',
            'zip': 'LT-01000',
            'company_registry': '123456',
            'phone': '+370 11 11 11 11',
            'country_id': cls.env.ref('base.lt').id,
            'vat': 'LT949170611'
        })

        cls.env['res.partner'].create({
            'name': 'Mr Big CEO',
            'is_company': False,
            'phone': '+370 11 11 12 34',
            'parent_id': cls.company_data['company'].partner_id.id,
        })

        cls.product_a.default_code = 'PA'
        cls.product_b.default_code = 'PB'

        # Create invoices

        invoices = cls.env['account.move'].create([{
                'move_type': 'out_invoice',
                'invoice_date': '2021-01-01',
                'date': '2021-01-01',
                'partner_id': cls.partner_a.id,
                'invoice_line_ids': [
                    Command.create({
                        'product_id': cls.product_a.id,
                        'quantity': 5.0,
                        'price_unit': 1000.0,
                        'tax_ids': [Command.set(cls.company_data['default_tax_sale'].ids)],
                    })
                ],
            },
            {
                'move_type': 'out_invoice',
                'invoice_date': '2021-03-01',
                'date': '2021-03-01',
                'partner_id': cls.company_data['company'].partner_id.id,
                'invoice_line_ids': [
                    Command.create({
                        'product_id': cls.product_a.id,
                        'quantity': 2.0,
                        'price_unit': 1500.0,
                        'tax_ids': [Command.set(cls.company_data['default_tax_sale'].ids)],
                    })
                ],
            },
            {
                'move_type': 'out_refund',
                'invoice_date': '2021-03-01',
                'date': '2021-03-01',
                'partner_id': cls.partner_a.id,
                'invoice_line_ids': [
                    Command.create({
                        'product_id': cls.product_a.id,
                        'quantity': 3.0,
                        'price_unit': 1000.0,
                        'tax_ids': [Command.set(cls.company_data['default_tax_sale'].ids)],
                    })
                ],
            },
            {
                'move_type': 'in_invoice',
                'invoice_date': '2021-06-30',
                'date': '2021-06-30',
                'partner_id': cls.partner_b.id,
                'invoice_line_ids': [
                    Command.create({
                        'product_id': cls.product_b.id,
                        'quantity': 10.0,
                        'price_unit': 800.0,
                        'tax_ids': [Command.set(cls.company_data['default_tax_purchase'].ids)],
                    })
                ],
            },
        ])
        invoices.action_post()

    @freeze_time('2022-01-01')
    def test_saft_report_values(self):
        report = self.env['account.general.ledger']
        options = self._init_options(report, fields.Date.to_date('2021-01-01'), fields.Date.to_date('2021-12-31'))

        with tools.file_open("l10n_lt_saft/tests/xml/expected_test_saft_report.xml", "rb") as expected_xml:
            self.assertXmlTreeEqual(
                self.get_xml_tree_from_string(report.get_xml(options)),
                self.get_xml_tree_from_string(expected_xml.read()),
            )
