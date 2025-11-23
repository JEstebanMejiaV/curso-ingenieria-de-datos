# Guía para instalar el comando `make` en Windows

Esta guía explica **dos formas** de usar el comando `make` en Windows:

- Opción A: Usar `make` dentro de **WSL (Ubuntu)**
- Opción B: Instalar `make` en **Windows nativo** con **Chocolatey**

Puedes usar la que prefieras. Si ya estás usando WSL, la opción recomendada es la **A**.

---

## Opción A: Usar `make` en WSL (Ubuntu)

### 1. Verificar que tienes WSL instalado

En **PowerShell** (no hace falta admin):

```powershell
wsl --list --online
```

Si ves distribuciones como `Ubuntu`, WSL está disponible.

Si no tienes ninguna distro instalada, puedes instalar Ubuntu con:

```powershell
wsl --install -d Ubuntu
```

Sigue las instrucciones en pantalla, crea tu usuario y contraseña de Ubuntu.
Si ya tienes Ubuntu instalado, pasa al siguiente paso.

---

### 2. Abrir Ubuntu

1. Ve al menú inicio de Windows.
2. Busca **“Ubuntu”**.
3. Ábrelo.

Deberías ver un prompt similar a:

```bash
tu_usuario@DESKTOP-XYZ:~$
```

---

### 3. Instalar `make` dentro de Ubuntu

En la ventana de **Ubuntu**:

```bash
sudo apt update
sudo apt install build-essential -y
```

`build-essential` instala `make` y otras herramientas de compilación.

Comprueba que está instalado:

```bash
make --version
```

Si ves algo como `GNU Make 4.x`, todo está bien.

---

### 4. Usar `make` en tu proyecto (desde WSL)

Tus archivos de Windows se ven en Ubuntu bajo `/mnt/c`.

Ejemplo: si tu proyecto está en:

```text
C:\Users\USER\Desktop\Git\curso-ingenieria-de-datos\modulo-02_bases_datos\Postgres
```

En Ubuntu:

```bash
cd /mnt/c/Users/USER/Desktop/Git/curso-ingenieria-de-datos/modulo-02_bases_datos/Postgres
ls
```

Ahora puedes usar:

```bash
make up
make seed
make down
```

---

## Opción B: Instalar `make` en Windows con Chocolatey

Esta opción es útil si quieres seguir usando **PowerShell** o **CMD** directamente, sin abrir Ubuntu.

### 1. Instalar Chocolatey

1. Abre **PowerShell como Administrador**
   - Inicio
   - Escribe `PowerShell`
   - Clic derecho en “Windows PowerShell”
   - “Ejecutar como administrador”

2. Ejecuta este comando (copiar y pegar):

```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force; `
[System.Net.ServicePointManager]::SecurityProtocol = `
[System.Net.ServicePointManager]::SecurityProtocol -bor 3072; `
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```

3. Cierra y vuelve a abrir PowerShell (puede ser sin admin).

---

### 2. Instalar `make` con Chocolatey

En PowerShell (normal):

```powershell
choco install make -y
```

Cuando termine, verifica:

```powershell
make --version
```

Si ves la versión de GNU Make, ya puedes usar `make` en cualquier carpeta que tenga un `Makefile`.

---

## Problemas frecuentes

### 1. “`make` no se reconoce como un comando interno o externo”

- Estás en **PowerShell/CMD** pero:
  - No instalaste `make`, o
  - Lo instalaste solo dentro de **WSL**, pero estás en Windows nativo.

Solución:

- Si instalaste `make` en WSL, siempre úsalo desde **Ubuntu**.
- Si quieres usarlo en PowerShell, instala `make` con **Chocolatey**.

### 2. Error de escritura (`meke`, `mkae`, etc.)

El comando debe escribirse exactamente:

```bash
make
```

Sin espacios extra, sin typos.

---

## Resumen rápido

- **Para entorno “tipo Linux” con Docker y proyectos de datos**  
  Usar WSL + Ubuntu y ejecutar:

  ```bash
  sudo apt update
  sudo apt install build-essential -y
  ```

- **Para usar `make` directo en PowerShell**  
  Instalar con Chocolatey:

  ```powershell
  choco install make -y
  ```

Con estas dos opciones, cualquier usuario de Windows puede tener `make` funcionando, ya sea en WSL o en el propio Windows.
