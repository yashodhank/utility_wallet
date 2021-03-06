# -*- coding: utf-8 -*-
# Copyright (c) 2017, Libermatic and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt

@frappe.whitelist()
def get_wallet_balance(wallet_provider=None, wallet_account=None):
    cond = []
    if wallet_provider:
        cond.append("against = '{}'".format(wallet_provider))
    if wallet_account:
        cond.append("account = '{}'".format(wallet_account))
    else:
        cond.append("account = '{}'".format(
                frappe.db.get_value('Utility Wallet Settings', None, 'wallet_account')))
    bal = frappe.db.sql("""
            SELECT sum(debit) - sum(credit)
            FROM `tabGL Entry`
            WHERE {}
        """.format(" and ".join(cond)))[0][0] or 0
    credit_amount = frappe.db.get_value('Supplier', wallet_provider, 'credit_amount') or 0
    return {
            'actual': flt(bal),
            'virtual': flt(bal + credit_amount)
        }

@frappe.whitelist()
def get_all_wallet_balances():
    data = []
    wallets = frappe.get_list("Supplier", fields=["name"], filters = { 'has_wallet': True })
    for w in wallets:
        balance = get_wallet_balance(w.name)
        credit_amount = frappe.db.get_value('Supplier', w.name, 'credit_amount')
        data.append({
                'wallet_provider': w.name,
                'actual_balance': balance['actual'],
                'virtual_balance': balance['virtual']
            })

    return data
