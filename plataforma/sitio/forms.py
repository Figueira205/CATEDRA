from django import forms


class SuscripcionForm(forms.Form):
    nombre = forms.CharField(max_length=120, required=False)
    email = forms.EmailField()
    consentimiento = forms.BooleanField(required=True)
    # Trampa para robots: un humano nunca rellena este campo oculto.
    web = forms.CharField(required=False)

    def clean(self):
        datos = super().clean()
        if datos.get("web"):
            raise forms.ValidationError("Envío no válido.")
        return datos
