from netforce.test import TestCase
from netforce.model import get_model
from datetime import *
import time

class Test(TestCase):
    _name="service.purchase.multi.pay"
    _string="Service purchase payment for 2 invoices"

    def test_run(self):
        # create invoice #1
        vals={
            "type": "in",
            "inv_type": "invoice",
            "partner_id": get_model("partner").search([["name","=","ABC Food"]])[0],
            "date": time.strftime("%Y-%m-%d"),
            "due_date": (datetime.now()+timedelta(days=30)).strftime("%Y-%m-%d"),
            "tax_type": "tax_ex",
            "lines": [("create",{
                "description": "Training",
                "qty": 1,
                "unit_price": 1000,
                "account_id": get_model("account.account").search([["name","=","Service Fee"]])[0],
                "tax_id": get_model("account.tax.rate").search([["name","=","Purchase Service - Company"]])[0],
                "amount": 1000,
            })],
        }
        inv1_id=get_model("account.invoice").create(vals,context={"type":"in","inv_type":"invoice"})
        inv=get_model("account.invoice").browse(inv1_id)
        inv.post()
        self.assertEqual(inv.state,"waiting_payment")
        move=inv.move_id
        self.assertEqual(move.lines[0].account_id.name,"Accounts Payable")
        self.assertEqual(move.lines[0].credit,1070)
        self.assertEqual(move.lines[1].account_id.name,"Suspend Input VAT")
        self.assertEqual(move.lines[1].debit,70)
        self.assertEqual(move.lines[2].account_id.name,"Service Fee")
        self.assertEqual(move.lines[2].debit,1000)

        # create invoice #2
        vals={
            "type": "in",
            "inv_type": "invoice",
            "partner_id": get_model("partner").search([["name","=","ABC Food"]])[0],
            "date": time.strftime("%Y-%m-%d"),
            "due_date": (datetime.now()+timedelta(days=30)).strftime("%Y-%m-%d"),
            "tax_type": "tax_ex",
            "lines": [("create",{
                "description": "Training",
                "qty": 1,
                "unit_price": 2000,
                "account_id": get_model("account.account").search([["name","=","Service Fee"]])[0],
                "tax_id": get_model("account.tax.rate").search([["name","=","Purchase Service - Company"]])[0],
                "amount": 2000,
            })],
        }
        inv2_id=get_model("account.invoice").create(vals,context={"type":"in","inv_type":"invoice"})
        inv=get_model("account.invoice").browse(inv2_id)
        inv.post()
        self.assertEqual(inv.state,"waiting_payment")
        move=inv.move_id
        self.assertEqual(move.lines[0].account_id.name,"Accounts Payable")
        self.assertEqual(move.lines[0].credit,2140)
        self.assertEqual(move.lines[1].account_id.name,"Suspend Input VAT")
        self.assertEqual(move.lines[1].debit,140)
        self.assertEqual(move.lines[2].account_id.name,"Service Fee")
        self.assertEqual(move.lines[2].debit,2000)

        # create payment for invoices #1 and #2
        vals={
            "partner_id": get_model("partner").search([["name","=","ABC Food"]])[0],
            "type": "out",
            "pay_type": "invoice",
            "date": time.strftime("%Y-%m-%d"),
            "account_id": get_model("account.account").search([["name","=","Saving Account -Kbank"]])[0],
            "lines": [
                ("create",{
                    "invoice_id": inv1_id,
                    "amount": 1070,
                    "tax_no": "1234",
                }),
                ("create",{
                    "invoice_id": inv2_id,
                    "amount": 2140,
                    "tax_no": "1235",
                }),
            ],
        }
        pmt_id=get_model("account.payment").create(vals,context={"type":"in"})
        pmt=get_model("account.payment").browse(pmt_id)
        pmt.post()
        inv1=get_model("account.invoice").browse(inv1_id)
        inv2=get_model("account.invoice").browse(inv2_id)
        self.assertEqual(pmt.state,"posted")
        self.assertEqual(inv1.state,"paid")
        self.assertEqual(inv2.state,"paid")
        move=pmt.move_id
        self.assertEqual(move.lines[0].account_id.name,"Saving Account -Kbank")
        self.assertEqual(move.lines[0].credit,3120)
        self.assertEqual(move.lines[1].account_id.name,"Accounts Payable")
        self.assertEqual(move.lines[1].debit,1070)
        self.assertEqual(move.lines[2].account_id.name,"Suspend Input VAT")
        self.assertEqual(move.lines[2].credit,70)
        self.assertEqual(move.lines[3].account_id.name,"Input VAT")
        self.assertEqual(move.lines[3].debit,70)
        self.assertEqual(move.lines[4].account_id.name,"Accounts Payable")
        self.assertEqual(move.lines[4].debit,2140)
        self.assertEqual(move.lines[5].account_id.name,"Suspend Input VAT")
        self.assertEqual(move.lines[5].credit,140)
        self.assertEqual(move.lines[6].account_id.name,"Input VAT")
        self.assertEqual(move.lines[6].debit,140)
        self.assertEqual(move.lines[7].account_id.name,"Accrued W/H Tax-Company (PND53)")
        self.assertEqual(move.lines[7].credit,90)

Test.register()
