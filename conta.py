# -*- coding: utf-8 -*-
"""
Created on Fri Oct  4 10:46:54 2019

@author: Jorge Edgar Rodriguez Ortiz Loyola 181334
"""
import datetime as dt


def iif(cond,vt,vf):
    if cond:
        res = vt
    else:
        res = vf
    return res  

# ============================================================================  
# ============================= Contabilidad =================================
# ============================================================================    

class Contabilidad:
   def __init__(self,empresa):
        self.empresa = empresa
        self.listaPartes=[0]*6  # nota: no se usa el espacio [0]
        self.listaPartes[1] = ParteContable(1,"Activo","D")
        self.listaPartes[2] = ParteContable(2,"Pasivo","A")
        self.listaPartes[3] = ParteContable(3,"Capital","A")
        self.listaPartes[4] = ParteContable(4,"Ingresos","A")
        self.listaPartes[5] = ParteContable(5,"Egresos","D")
        self.listaPolizas=[]
        self.act=None
        

   def altaCta(self,numCta,nombreCta,natCta):
       numParte = numCta // 100000
       if 1 <= numParte <= 5:
          self.listaPartes[numParte].altaCta(numCta,nombreCta,natCta)
       else:
          raise Exception("Contabilidad: el número de cuenta no es válido")
   
       
   def registraPoliza(self,poliza):
       # verificamos que suma de cargos sea igual a suma de abonos
       sc = 0
       sa = 0
       for m in poliza.colMovtos:
           if m.tipo == "A":
               sa += m.monto
           elif m.tipo == "C":
               sc += m.monto
           else:
               raise Exception("Tipo de movimiento inválido " + str(m))
       if sa != sc :
           raise Exception("Póliza " + str(poliza) + " ==== DESBALANCEADA ===" )
           
       # verificamos que todas las cuentas de los movimientos de la poliza existan
       for m in poliza.colMovtos:
           numParte = m.numCta // 100000
           if 1 <= numParte <= 5:
               # la parte contable arroja una excepción si la cta no existe
               self.listaPartes[numParte].verificaExistencia(m.numCta)
           else:
               raise Exception("La cta del movimiento " + str(m) + " es inválida" )
       self.listaPolizas.append(poliza)
       
       # registramos los movimientos
       for m in poliza.colMovtos:
           numParte = m.numCta // 100000
           self.listaPartes[numParte].registraMovto(m)
           
   def polizasRegistradas(self):
       for x in  self.listaPolizas:
           print(x)
          
           
   def impBalance(self):  
       strRes = "\nBalance de " + self.empresa + '\n' 
       for p in self.listaPartes[1:]:
            strRes += p.impBalance()
       strRes += 61 * '-' + '\n'     
       strRes +=  "Activo = \tPasivo \t+ Capital \t+ Ingresos \t- Egresos\n"
       strRes += str(self.listaPartes[1].saldo().monto) + " = \t" + str(self.listaPartes[2].saldo().monto) + " \t+ " + str(self.listaPartes[3].saldo().monto) + " \t+ " + str(self.listaPartes[4].saldo().monto) + " \t- " + str(self.listaPartes[5].saldo().monto) + "\n"  
       strRes += str(self.listaPartes[1].saldo().monto) + " = " + str(self.listaPartes[2].saldo().monto+self.listaPartes[3].saldo().monto+self.listaPartes[4].saldo().monto-self.listaPartes[5].saldo().monto)+"\n"    
       strRes += 61 * '-' + '\n'  
       return strRes
   
   def __str__(self):
       strRes = "Contabilidad " + self.empresa + '\n'
       for x in self.listaPartes[1:]:
           strRes += str(x)
       return strRes
   def creaPoliza(self,numeroPoliza,descripcion):
       self.act= PolizaContable(numeroPoliza,dt.datetime.today().strftime("%Y%m%d_%H%M%S"), descripcion)
   
   def abono(self,numCta, cantidad):
       if self.act != None:
           self.act.abono(numCta,cantidad)
           
   def cargo(self,numCta, cantidad):
       if self.act != None:
           self.act.cargo(numCta,cantidad)   
           
   def registraPolizaConta(self):
          # verificamos que suma de cargos sea igual a suma de abonos
       poliza=self.act
       sc = 0
       sa = 0
       for m in poliza.colMovtos:
           if m.tipo == "A":
               sa += m.monto
           elif m.tipo == "C":
               sc += m.monto
           else:
               raise Exception("Tipo de movimiento inválido " + str(m))
       if sa != sc :
           raise Exception("Póliza " + str(poliza) + " ==== DESBALANCEADA ===" )
           
       # verificamos que todas las cuentas de los movimientos de la poliza existan
       for m in poliza.colMovtos:
           numParte = m.numCta // 100000
           if 1 <= numParte <= 5:
               # la parte contable arroja una excepción si la cta no existe
               self.listaPartes[numParte].verificaExistencia(m.numCta)
           else:
               raise Exception("La cta del movimiento " + str(m) + " es inválida" )
       self.listaPolizas.append(poliza)
       
       # registramos los movimientos
       for m in poliza.colMovtos:
           numParte = m.numCta // 100000
           self.listaPartes[numParte].registraMovto(m)
           
   def cierre(self):
       #2.1) Verificar que exista la cuenta "300100 Resultado del Ejercicio (A), en caso de no existir, darla de alta;
       
       self.altaCta(300100,"Resultado del ejercicio","A")

       #2.2) Crear la póliza de cierre (número 1000, fecha y hora del momento, "Cierre del Ejercicio"), para la fecha y hora del momento ver la instrucción en las pólizas del script);
       
       polizaCierre= PolizaContable(1000, dt.datetime.today().strftime("%Y%m%d_%H%M%S"),"Cierre del Ejercicio")
       
       #2.3) Saldar a cero las cuentas de Ingreso, mandando el movimiento de saldo a cero para la cuenta en cuestión y el contra movimiento a la cuenta de Resultado del Ejercicio;
       #2.4) De manera similar saldar a cero las cuentas de Egresos;
       cantIn=self.listaPartes[4].saldo().monto
       cantEg=self.listaPartes[5].saldo().monto
       cantTotal= cantIn - cantEg
       polizaCierre.abono(300100, cantTotal)
       self.listaPartes[4].cierre(polizaCierre)
       self.listaPartes[5].cierre(polizaCierre)
       #2.5) Incidir la póliza de cierre
       self.registraPoliza(polizaCierre)
       
    
# ============================================================================  
# ============================ ParteContable =================================
# ============================================================================    
   
class ParteContable:
    def __init__(self, numParte, nombreParte,natParte):
        self.num    = numParte
        self.nombre = nombreParte
        self.nat    = natParte
        self.colCtas = {}
     
    def altaCta(self,numCta,nombreCta, natCta):
        if self.colCtas.get(numCta) == None:
            self.colCtas[numCta] = CtaT(numCta,nombreCta,natCta)
        else:
            raise Exception("La cuenta " + numCta + " " + nombreCta + " (" + natCta + ") ya existe")
    def verificaExistencia(self,numCta):
        if self.colCtas.get(numCta) == None:
            raise Exception("La cta " + str(numCta) + " no existe")
    
    def registraMovto(self,m):
         cta = self.colCtas.get(m.numCta)
         cta.registraMovto(m)

    def saldo(self):
        sdoCtasD = 0
        sdoCtasA = 0
        for cta in self.colCtas.values():
            if cta.nat == "D":
                sdoCtasD += cta.saldo().monto
            else:
                sdoCtasA += cta.saldo().monto
        if self.nat == "D":
            m_sdo = MovtoConta(0,1,sdoCtasD - sdoCtasA,"C")
        else:
            m_sdo = MovtoConta(0,1,sdoCtasA - sdoCtasD,"A")
        return m_sdo
           
    def impSaldo(self):
        sdo = self.saldo()
        strRes = iif(sdo.tipo=='A',39,23) * ' ' + '{:12.2f}'.format(sdo.monto) + '\n'
        return strRes
    
    def impBalance(self): 
       strRes = '_' * 61 + '\n' + \
                '{:25}'.format(str(self.num) + '(' + self.nat + ') ' + self.nombre + 5*' ') + '\n'
       for cta in self.colCtas.values():
           strRes += cta.impBalance()
       strRes += '=' * 61  +'\n'  
       strRes += '**********' + self.impSaldo()
       return strRes   
    def cierre(self, polC):
        for cta in self.colCtas.values():
            tot=cta.saldo().monto
            if self.nat=="D":
                polC.abono(cta.num, tot)
            else:
                polC.cargo(cta.num, tot)

                
    def __str__(self):
       strRes = '_' * 51 + '\n' + \
                '{:37}'.format("Parte Contable " + str(self.num) + " " + self.nombre) + \
                " (" + self.nat + ")\n"          
       for cta in self.colCtas.values():
           strRes += str(cta)
       strRes += ' ' + self.impSaldo()    
       return strRes    

# ============================================================================  
# ================================ CtaT ======================================
# ============================================================================    

class CtaT:
    def __init__(self,numCta,nombreCta,natCta):
        self.num = numCta
        self.nombre = nombreCta
        self.nat = natCta
        self.colMovtos = []
        
    def registraMovto(self,m):
        self.colMovtos.append(m)
    
    def saldo(self):
        sc = 0
        sa = 0
        for m in self.colMovtos:
            if m.tipo == "C":
                sc += m.monto
            else:
                sa += m.monto
        if self.nat == "D":
            m_sdo = MovtoConta(0,1,sc - sa,"C")
        else:
            m_sdo = MovtoConta(0,1,sa - sc,"A")
        return m_sdo   
    
    def impBalance(self):
        sdo = self.saldo()
        strRes = "  " + \
                '{:27}'.format(str(self.num) + ' ' + self.nombre) + ' (' + self.nat + ')' 
        strRes += iif(sdo.tipo=='A',16,0) * ' ' + '{:12.2f}'.format(sdo.monto) + '\n'
        return strRes

    def impSaldo(self):
        sdo = self.saldo()
        strRes = iif(sdo.tipo=='A',40,24) * ' ' + '{:12.2f}'.format(sdo.monto)
        return strRes

    
    def __str__(self):
        strRes = "  " + \
                '{:36}'.format(str(self.num) + ' ' + self.nombre) + \
                '(' + self.nat + ')' + '\n' + \
                51 * '-' + '\n'
        for m in self.colMovtos:
            strRes += str(m)
        if len(self.colMovtos) > 0:
          strRes += 51 * '-' + '\n'    
        strRes += self.impSaldo() + '\n'
        strRes += 51 * '-' + '\n'  
        return strRes

# ============================================================================  
# ============================= PolizaContable ===============================
# ============================================================================    

class PolizaContable:
    def __init__(self,numPoliza,fecha,descripcion):
        self.numPoliza   = numPoliza
        self.fecha       = fecha
        self.descripcion = descripcion
        self.colMovtos = []
        
    def cargo(self,numCta,monto):
        self.colMovtos.append(MovtoConta(self.numPoliza,numCta,monto,'C'))
    def abono(self,numCta,monto):
        self.colMovtos.append(MovtoConta(self.numPoliza,numCta,monto,'A'))
        
    def __str__(self):
        strRes = "Póliza num " + str(self.numPoliza) + " " + self.fecha + " " + self.descripcion + '\n'
        for m in self.colMovtos:
            strRes += str(m) 
        return strRes    

# ============================================================================  
# ============================== MovtoConta ==================================
# ============================================================================    
            
class MovtoConta:
    def __init__(self,numPoliza,numCta,monto,c_a):
        self.numPoliza = numPoliza
        self.numCta    = numCta
        self.monto     = monto
        self.tipo      = c_a
        
    def __str__(self):
        strRes = "  " + '{:5d}'.format(self.numPoliza) + ')' + 5*' ' + str(self.numCta)
        strRes += iif(self.tipo == "A", 21,5) * ' '
        strRes += '{:12.2f}'.format(self.monto) + '\n'
        return strRes 
           
# =======================================================================================
#                                         script de prueba         
# =======================================================================================

cu='181334'
nombre='Rodriguez Ortiz Loyola Jorge Edgar'

print('CU:',cu,'Nombre:',nombre)

conta = Contabilidad("Empre S.A. de " + nombre)
conta.altaCta(100100,"Bancos","D")
conta.altaCta(100200,"Inventario","D")
conta.altaCta(100300,"Clientes","D")
conta.altaCta(200100,"Proveedores","A")
conta.altaCta(300000,"Capital","A")
conta.altaCta(400100,"Ventas","A")
conta.altaCta(500100,"Costo de lo vendido","D")
print('Posterior al alta de las cuentas')
print(conta)        
print("===============================================")
pol_1 = PolizaContable(1,dt.datetime.today().strftime("%Y%m%d_%H%M%S"), "Creación de la empresa")
pol_1.cargo(100100,10000.0)
pol_1.abono(300000,10000.0)
print(pol_1)
print("===============================================")
try:
  conta.registraPoliza(pol_1)
except Exception as ex:
  print(ex.args[0])
finally:  
  print('Posterior al registro de la póliza 1')
  print(conta)
print("===============================================")
pol_2 = PolizaContable(2,dt.datetime.today().strftime("%Y%m%d_%H%M%S"),"Compra de mercancía para vender")
pol_2.abono(100100,5000.0) # Se paga al contado
pol_2.cargo(100200,5000.0) # Se guarda en el almacen (Inventario)
print("===============================================")
try:
  conta.registraPoliza(pol_2)
except Exception as ex:
  print(ex.args[0])
finally:  
  print('Posterior al registro de la póliza 2')
  print(conta)
print("++++++++++++++++++++++++++++++++++++++++++++++++")
pol_3 = PolizaContable(3,dt.datetime.today().strftime("%Y%m%d_%H%M%S"),"Venta en 1500.0, al contado de mercancia que costó 1000.0")
pol_3.abono(100200,1000.0)
pol_3.cargo(500100,1000.0)
pol_3.abono(400100,1500.0)
pol_3.cargo(100100,1500.0)
print("===============================================")
try:
  conta.registraPoliza(pol_3)
except Exception as ex:
  print(ex.args[0])
finally:  
  print('Posterior al registro de la póliza 3')
  print(conta)

print("+++++++++++++++++++++++++++++++++++++++++++++++++++++")
pol_4 = PolizaContable(4,dt.datetime.today().strftime("%Y%m%d_%H%M%S"),"Venta en 1000.0, al contado de mercancia que costó 750.0")
pol_4.abono(100200,750.0)
pol_4.cargo(500100,750.0)
pol_4.abono(400100,1000.0)
pol_4.cargo(100100,1000.0)
print("===============================================")
try:
  conta.registraPoliza(pol_4)
except Exception as ex:
  print(ex.args[0])
finally:  
  print('Posterior al registro de la póliza 4')
  print(conta)
print('>>>>>>>> [2.5] Ejer_1: Implementar la eciacón del balance A=P+C+I-E')
print("+++++++++++++++++++++++++++++++++++++++++++++++++++++")
print( conta.impBalance())
print("+++++++++++++++++++++++++++++++++++++++++++++++++++++")
print()
print('>>>>>>>> [3.5] Ejer_2: Implementar el cierre del ejercicio')
print('Cierre del ejercicio')
conta.cierre()
print()
print("+++++++++++++++++++++++++++++++++++++++++++++++++++++")
print('Posterior al cierre:')
print( conta.impBalance())
print("+++++++++++++++++++++++++++++++++++++++++++++++++++++")
print()
print('>>>>>>>> [2.5] Ejer_3: La póliza debe guardar las pólizas aceptadas en una colección')
print()
#
conta.polizasRegistradas() # despliega las pólizas registradas
#
print('>>>>>>>> [1.5] Ejer_4: La contabilidad administra la creación de la póliza y la creación de los movimientos')
print()
#
conta.creaPoliza(5,"Aumento de Capital") #el timestamp lo maneja la contabilidad
conta.abono(300000,5000.00)
conta.cargo(100100,5000.00)
try:
  conta.registraPolizaConta()
  print("Registro Exitoso")
except Exception as ex:
  print(ex.args[0])

print('====================== STATUS FINAL =================')
print(conta)


#
#
#
#