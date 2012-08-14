from common import Request

class SocialInteractionRequest(Request):

    type = Request.TYPE_SOCIAL

    def build_parameters(self):
        p = super(SocialInteractionRequest, self).build_parameters()

        p.utmsn = self.social_interaction.network
        p.utmsa = self.social_interaction.action
        p.utmsid = self.social_interaction.target
        if not p.utmsid:
            # Default to page path like ga.js
            p.utmsid = self.page.path

        return p
