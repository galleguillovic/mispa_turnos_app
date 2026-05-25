# 👩🏼‍💻 Aplicación MiSpa Turnos 

*Esta aplicación es un sistema de gestión de turnos para el salón de belleza Macaspa, desarrollado como Trabajo Final de la Tecnicatura Universitaria en Informática (TUI) — Universidad Nacional de La Rioja (UNLaR)..*
#### 👓 Autora
Victoria Antonela Galleguillo
Tecnicatura Universitaria en Informática — UNLaR

## 🌸 Descripción de la aplicación

MiSpa Turnos es una aplicación de escritorio que permite gestionar turnos, clientes, empleados y servicios de forma digital, reemplazando las practicas rudimentarias y manuales. El sistema cuenta con dos roles de usuario: administrador (gestión completa) y usuario estándar (acceso a sus propios turnos y vistas de solo lectura).

## 👾 Tecnologías usadas

| Tecnología  | Uso |
| ------------- |:-------------:|
| Python 3.122     | Lenguaje de programación   |
| Tkinter  | Interfaz gráfica     |
| MySQL 8.0      | Base de Datos     |
| Pillow  | Procesamiento de imagenes     |
| mysql-connector-python   | Conexión a la base de datos     |
| tkcalendar    | Calendario interactivo   |
| ReportLab | Generación de reportes en PDF     |
| bcrypt  | Hasheo de contraseñas |
| PyInstaller  | Empaquetado en ejecutable |

## 📁 Estructura del proyecto
``mispa_turnos_app/``\
``├── main.py  *Punto de entrada*``\
``├── config.ini *Configuración de conexión a la BD*``\
``├── assets/ *Imágenes e íconos*``\
``├── db/  *Conexión a la base de datos*``\
``├── modelos/ *Autenticación de usuarios*``\
``├── utils/   *Funciones auxiliares (hasheo)*``\
``└── vistas/ *Todas las pantallas de la aplicación*``\


## 🛠️ Instalación y configuración

### Requisitos previos
+ Windows 10/11 de 64 bits
+ MySQL instalado y en ejecución

### Paso 1 - Importar la base de datos

1. Abrí MySQL Workbench
2. Conectate a tu servidor MySQL local
3. En el menú: Server > Data Import
4. Seleccioná Import from Self-Contained File
5. Elegí el archivo mispa_turnos.sql
6. En Default Target Schema escribí mispa_turnos
7. Hacé clic en Start Import\
O bien desde la terminal:
```
mysql -u root -p < mispa_turnos.sql
```
### Paso 2 - Configurar conexión
Editar el archivo config.ini con las credenciales de tu servidor MySQL.
```
[database]
host = 127.0.0.1
user = root
password = tu_contraseña
database = mispa_turnos
```
### Paso 3 - Ejecutar la aplicación
Copiá la carpeta de distribución a una ubicación fija (por ejemplo C:\MiSpa Turnos\) y creá un acceso directo al archivo MiSpa Turnos.exe en el escritorio.
```
Importante: el ejecutable debe permanecer dentro de su carpeta original. No puede moverse de forma independiente. Si desea verlo desde el escritorio, debe crear un acceso directo.
```

## 🌐 Credenciales por defecto
| Campo  | Valor |
| ------------- |:-------------:|
| Usuario     | admin     |
| Contraseña   | admin1234     |

```
Cambiar la contraseña al ingresar por primera vez desde Configurar Perfil
```

## 🔑 Ejecución desde código fuente
Instalar las dependencias:
```
pip install pillow mysql-connector-python tkcalendar reportlab bcrypt babel
```
Ejecutar la aplicación:
```
python main.py
```
#### Generar el ejecutable
Si clonas mi directorio de git, y quieres generar el ejecutable, escribe este comando desde la terminal:
```
python -m PyInstaller --noconfirm --onedir --windowed \
  --name "MiSpa Turnos" \
  --icon "assets/logo_mispa.ico" \
  --add-data "assets;assets" \
  --add-data "config.ini;." \
  --add-data "vistas;vistas" \
  --add-data "modelos;modelos" \
  --add-data "db;db" \
  --add-data "utils;utils" \
  --hidden-import mysql.connector \
  --hidden-import mysql.connector.plugins \
  --hidden-import mysql.connector.plugins.mysql_native_password \
  --hidden-import PIL --hidden-import PIL.Image \
  --hidden-import PIL.ImageTk --hidden-import PIL.ImageDraw \
  --hidden-import tkcalendar --hidden-import babel.numbers \
  --hidden-import bcrypt \
  --collect-all mysql \
  main.py
```
Asegurate que la carpeta assets/ esté dentro de dist/MiSpa Turnos/.
Si no lo está copiala manualmente.