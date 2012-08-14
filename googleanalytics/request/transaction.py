from common import Request

class TransactionRequest(Request):

    type = Request.TYPE_TRANSACTION

    def build_parameters(self):
        p = super(TransactionRequest, self).build_parameters()

        p.utmtid = self.transaction.order_id
        p.utmtst = self.transaction.affiliation
        p.utmtto = self.transaction.total
        p.utmttx = self.transaction.tax
        p.utmtsp = self.transaction.shipping
        p.utmtci = self.transaction.city
        p.utmtrg = self.transaction.region
        p.utmtco = self.transaction.country

        return p

    def build_visitor_parameters(p):
        return p

    def build_customvariables_parameter(p):
        return p

