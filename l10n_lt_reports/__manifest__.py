# Author: Eimantas Nėjus. Copyright: JSC Focusate.
# Co-Authors: Silvija Butko, Andrius Laukavičius. Copyright: JSC Focusate
# See LICENSE file for full copyright and licensing details.
{
    'name': 'Lithuania - Accounting Reports',
    'icon': '/l10n_lt/static/description/icon.png',
    'version': '1.0.0',
    'description': """
        Accounting reports for Lithuania

        Contains Balance Sheet, Profit/Loss reports
    """,
    'license': 'OEEL-1',
    'author': "Focusate",
    'website': "http://www.focusate.eu",
    'category': 'Accounting/Localizations/Reporting',
    'depends': [
        'account_reports',
        'l10n_lt'
    ],
    'data': [
        'data/account_financial_html_report_data.xml',
    ],
    'auto_install': True,
    'installable': True,
}
