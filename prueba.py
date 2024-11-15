from experta import *
import wx

class VentanaRecomendaciones(wx.Frame):
    def __init__(self, parent, recomendacion):
        super().__init__(parent, title="Recomendaciones", size=(400, 300))
        
        panel = wx.Panel(self)
        
        wx.StaticText(panel, label=f"Recomendación: {recomendacion}", pos=(20, 20))
        
        self.cerrar_btn = wx.Button(panel, label="Cerrar", pos=(150, 200))
        self.cerrar_btn.Bind(wx.EVT_BUTTON, self.on_cerrar)
        
        self.Show()
        
    def on_cerrar(self, event):
        self.Close()

class VentanaPrincipal(wx.Frame):
    def __init__(self, *args, **kw):
        super(VentanaPrincipal, self).__init__(*args, **kw)
        
        panel = wx.Panel(self)
        self.SetSize((500, 450))
        self.SetTitle("Datos del Cliente")

        wx.StaticText(panel, label="Nombre y Apellido", pos=(20, 20))
        self.nombre_apellido = wx.TextCtrl(panel, pos=(20, 40), size=(200, -1))

        wx.StaticText(panel, label="Edad", pos=(20, 80))
        self.edad = wx.TextCtrl(panel, pos=(20, 100), size=(200, -1))

        wx.StaticText(panel, label="Año de Antigüedad", pos=(20, 140))
        self.antiguedad = wx.TextCtrl(panel, pos=(20, 160), size=(200, -1))

        wx.StaticText(panel, label="Ingreso Base Mensual", pos=(20, 200))
        self.ingreso_base = wx.TextCtrl(panel, pos=(20, 220), size=(200, -1))

        wx.StaticText(panel, label="Grado de incapacidad", pos=(20, 260))
        self.grado_incapacidad = wx.TextCtrl(panel, pos=(20, 280), size=(200, -1))

        wx.StaticText(panel, label="Cliente tiene ART:", pos=(250, 20))
        self.art_hidden = wx.RadioButton(panel, label="", pos=(-100, -100), style=wx.RB_GROUP)
        self.art_si = wx.RadioButton(panel, label="Sí", pos=(250, 40))
        self.art_no = wx.RadioButton(panel, label="No", pos=(250, 60))

        wx.StaticText(panel, label="Patologías Previas:", pos=(250, 100))
        self.patologias_previas_hidden = wx.RadioButton(panel, label="", pos=(-100, -100), style=wx.RB_GROUP)
        self.patologias_previas_si = wx.RadioButton(panel, label="Sí", pos=(250, 120))
        self.patologias_previas_no = wx.RadioButton(panel, label="No", pos=(250, 140))

        wx.StaticText(panel, label="Documentación Médica:", pos=(250, 180))
        self.documentacion_medica_hidden = wx.RadioButton(panel, label="", pos=(-100, -100), style=wx.RB_GROUP)
        self.documentacion_medica_si = wx.RadioButton(panel, label="Sí", pos=(250, 200))
        self.documentacion_medica_no = wx.RadioButton(panel, label="No", pos=(250, 220))

        wx.StaticText(panel, label="Tipo (Accidente o Enfermedad):", pos=(250, 260))
        self.tipo = wx.Choice(panel, choices=["Accidente", "Enfermedad"], pos=(250, 280))

        self.boton_procesar = wx.Button(panel, label="Evaluar", pos=(200, 350))
        self.boton_procesar.Bind(wx.EVT_BUTTON, self.on_procesar)

    def calcular_monto(self, ingreso_base, grado_incapacidad, edad):
        return (53 * ingreso_base) * (grado_incapacidad / 100) * (65 / edad)

    def on_procesar(self, event):
        nombre_apellido = self.nombre_apellido.GetValue()
        edad = int(self.edad.GetValue())
        antiguedad = int(self.antiguedad.GetValue())
        ingreso_base = int(self.ingreso_base.GetValue())
        grado_incapacidad = int(self.grado_incapacidad.GetValue())
        art = self.art_si.GetValue()
        patologias_previas = self.patologias_previas_si.GetValue()
        documentacion_medica = self.documentacion_medica_si.GetValue()
        tipo = self.tipo.GetStringSelection()

        Motor = MotorInferencia(edad, ingreso_base, grado_incapacidad)
        Motor.reset()
        Motor.declare(datos(Nombre_apellido=nombre_apellido, Edad=edad, Antiguedad=antiguedad, ART=art, Patologias=patologias_previas, Documentacion=documentacion_medica, Tipo=tipo, grado_incapacidad=grado_incapacidad))
        Motor.run()
        recomendacion = f"Recomendación para {nombre_apellido}: {Motor.recomendacion}"
        self.ventana_recomendaciones = VentanaRecomendaciones(self, recomendacion)


class datos(Fact):
    Estado_Trabajo = Field(bool)
    Antiguedad = Field(int)
    viabilidad = Field(int)
    grado_incapacidad = Field(int)
    pass

class MotorInferencia(KnowledgeEngine):
    recomendacion = "En evaluación"

    def __init__(self, edad, ingreso_base, grado_incapacidad):
        super().__init__()
        self.edad = edad
        self.ingreso_base = ingreso_base
        self.grado_incapacidad = grado_incapacidad

    @Rule(datos(ART=True))
    def R1(self):
        self.declare(datos(Estado_Trabajo=True))

    @Rule(datos(ART=False))
    def R2(self):
        self.declare(datos(Estado_Trabajo=False))

    @Rule(datos(Estado_Trabajo=False))
    def R3(self):
        self.declare(datos(viabilidad=3))

    @Rule(datos(Estado_Trabajo=True) & datos(Antiguedad=P(lambda Antiguedad: Antiguedad < 3)))
    def R4(self):
        self.declare(datos(viabilidad=2))

    @Rule(datos(Estado_Trabajo=True) & datos(Patologias=False) & datos(Antiguedad=P(lambda Antiguedad: Antiguedad > 3)))
    def R5(self):
        self.declare(datos(viabilidad=1))

    @Rule(datos(Estado_Trabajo=True) & datos(Patologias=True))
    def R6(self):
        self.declare(datos(viabilidad=2))

    @Rule(datos(Estado_Trabajo=True) & datos(Tipo="Accidente") | datos(Tipo="Enfermedad") & datos(Documentacion=False))
    def R7(self):
        self.declare(datos(viabilidad=2))

    @Rule(datos(Estado_Trabajo=True) & datos(Tipo="Accidente") | datos(Tipo="Enfermedad") & datos(Documentacion=True))
    def R8(self):
        self.declare(datos(viabilidad=1))

    @Rule(datos(viabilidad=1) & datos(grado_incapacidad=P(lambda gi: gi < 50)))
    def R9(self):
        monto = VentanaPrincipal.calcular_monto(self, self.ingreso_base, self.grado_incapacidad, self.edad)
        self.recomendacion = f"La recomendación es la n°1 y el monto calculado es {monto}"

    @Rule(datos(viabilidad=1) & datos(grado_incapacidad=P(lambda gi: gi >= 50)))
    def R10(self):
        monto = VentanaPrincipal.calcular_monto(self, self.ingreso_base, self.grado_incapacidad, self.edad)
        self.recomendacion = f"La recomendación es la n°2 y el monto calculado es {monto}"

    @Rule(datos(viabilidad=2))
    def R11(self):
        self.recomendacion = "La recomendación es la n°3"

    @Rule(datos(viabilidad=3))
    def R12(self):
        self.recomendacion = "La recomendación es la n°4"

if __name__ == "__main__":
    app = wx.App()
    ventana_principal = VentanaPrincipal(None)
    ventana_principal.Show()
    app.MainLoop()
