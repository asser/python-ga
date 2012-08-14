from common import Request

class ItemRequest(Request):

    type = Request.TYPE_ITEM

    def build_parameters(self):
        p = super(ItemRequest, self).build_parameters()

        p.utmtid = self.item.order_id
        p.utmipc = self.item.sku
        p.utmipn = self.item.name
        p.utmiva = self.item.variation
        p.utmipr = self.item.price
        p.utmiqt = self.item.quantity

        return p

    def build_visitor_parameters(p):
        return p

    def build_customvariables_parameter(p):
        return p

