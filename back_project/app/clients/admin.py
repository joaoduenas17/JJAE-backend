from django.contrib import admin
from .models import Client, Setting, WebService, FAQ, \
    SocialNetwork, TextGeneralCondition, TextTermsCondition, SingleColor, \
    NewsLetterSubscription, ExternalOauth2, ClientFAQ
    


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['name', 'get_sites']
    exclude = ('update_client_status',)

    def get_sites(self, obj):
        return "\n".join([c.domain for c in obj.sites.all()])


@admin.register(Setting)
class SettingAdmin(admin.ModelAdmin):
    pass



@admin.register(WebService)
class WebServiceAdmin(admin.ModelAdmin):
    pass



@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    pass



@admin.register(ClientFAQ)
class ClientFAQAdmin(admin.ModelAdmin):
     pass


@admin.register(SocialNetwork)
class SocialNetworkAdmin(admin.ModelAdmin):
    pass


@admin.register(TextGeneralCondition)
class TextGeneralConditionAdmin(admin.ModelAdmin):
    pass


@admin.register(TextTermsCondition)
class TextTermsConditionAdmin(admin.ModelAdmin):
    pass



@admin.register(SingleColor)
class SingleColorAdmin(admin.ModelAdmin):
    pass





@admin.register(NewsLetterSubscription)
class NewsLetterSubscriptionAdmin(admin.ModelAdmin):
    pass




@admin.register(ExternalOauth2)
class ExternalOauth2Admin(admin.ModelAdmin):
    pass
