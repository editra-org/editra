;------------------------------------------------------------------------------
; Editra Windows Installer Build Script
; Language: NSIS
; 
;------------------------------------------------------------------------------


;------------------------------ Start MUI Setup -------------------------------

; Global Variables
!define PRODUCT_NAME "Editra"
!define PRODUCT_VERSION "0.2.50"
!define PRODUCT_PUBLISHER "Cody Precord"
!define PRODUCT_WEB_SITE "http://editra.org"
!define PRODUCT_DIR_REGKEY "Software\Microsoft\Windows\CurrentVersion\App Paths\Editra.exe"
!define PRODUCT_UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"
!define PRODUCT_UNINST_ROOT_KEY "HKLM"

SetCompressor lzma

; MUI 1.67 compatible ------
!include "MUI.nsh"

; MUI Settings
!define MUI_ABORTWARNING
!define MUI_ICON "pixmaps\editra.ico"
!define MUI_UNICON "pixmaps\editra.ico"

; Welcome page
!insertmacro MUI_PAGE_WELCOME

; License page (Read the Licence)
!insertmacro MUI_PAGE_LICENSE "COPYING"

; Directory page (Set Where to Install)
!insertmacro MUI_PAGE_DIRECTORY

; Instfiles page (Do the installation)
!insertmacro MUI_PAGE_INSTFILES

; Finish page (Post installation tasks)
!define MUI_FINISHPAGE_RUN
!define MUI_FINISHPAGE_RUN_TEXT "Run Editra"
!define MUI_FINISHPAGE_RUN_FUNCTION "LaunchEditra"
;!define MUI_FINISHPAGE_SHOWREADME
;!define MUI_FINISHPAGE_SHOWREADME_TEXT "Add 'Open With' Shell Extension"
;!define MUI_FINISHPAGE_SHOWREADME_FUNCTION "AddOpenWith"
!insertmacro MUI_PAGE_FINISH

; Uninstaller pages
!insertmacro MUI_UNPAGE_INSTFILES

; Language files
!insertmacro MUI_LANGUAGE "English"

; Reserve files
!insertmacro MUI_RESERVEFILE_INSTALLOPTIONS

;------------------------------- End MUI Setup --------------------------------

 
;------------------------------ Start Installer -------------------------------

;---- Constants
Name "${PRODUCT_NAME} ${PRODUCT_VERSION}"
OutFile "editra.win32.${PRODUCT_VERSION}.exe"
InstallDir "$PROGRAMFILES\Editra"
InstallDirRegKey HKLM "${PRODUCT_DIR_REGKEY}" ""
ShowInstDetails show
ShowUnInstDetails show

; Prepare for installation
;Function .onInit
;  ;Extract InstallOptions INI files
;  !insertmacro MUI_INSTALLOPTIONS_EXTRACT "ftypeopts.ini"
;FunctionEnd

; Check that Editra is not running when starting the installation
Section "MainSection" SEC01
  FindProcDLL::FindProc "Editra.exe"
  StrCmp $R0 0 continueInstall
    MessageBox MB_ICONSTOP|MB_OK "${PRODUCT_NAME} is still running please close all running instances and try to install again"
    Abort
  continueInstall:
SectionEnd

; Extract the files from the installer to the install location
Section "MainSection" SEC02
  SetOverwrite try
  SetOutPath "$INSTDIR\"
  File /r ".\*.*"
  CreateDirectory "$SMPROGRAMS\Editra"
  CreateShortCut "$SMPROGRAMS\Editra\Editra.lnk" "$INSTDIR\Editra.exe"
  CreateShortCut "$DESKTOP\Editra.lnk" "$INSTDIR\Editra.exe"
SectionEnd

; Make/Install Shortcut links
Section -AdditionalIcons
  WriteIniStr "$INSTDIR\${PRODUCT_NAME}.url" "InternetShortcut" "URL" "${PRODUCT_WEB_SITE}"
  CreateShortCut "$SMPROGRAMS\Editra\Website.lnk" "$INSTDIR\${PRODUCT_NAME}.url"
  CreateShortCut "$SMPROGRAMS\Editra\Uninstall.lnk" "$INSTDIR\uninst.exe"
SectionEnd

; Post installation setup
Section -Post
  ;---- Write registry keys for uninstaller
  WriteUninstaller "$INSTDIR\uninst.exe"
  WriteRegStr HKLM "${PRODUCT_DIR_REGKEY}" "" "$INSTDIR\Editra.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayName" "$(^Name)"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "UninstallString" "$INSTDIR\uninst.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayIcon" "$INSTDIR\Editra.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayVersion" "${PRODUCT_VERSION}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "URLInfoAbout" "${PRODUCT_WEB_SITE}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "Publisher" "${PRODUCT_PUBLISHER}"
SectionEnd

; Called if Run Editra is checked on the last page of installer
Function LaunchEditra
  Exec '"$INSTDIR\Editra.exe" "$INSTDIR\CHANGELOG" '
FunctionEnd

; Called if Add openwith entry is checked (FINSHPAGE_SHOWREADME)
;Function AddOpenWith

;  ; Notify of the shell extension changes
;  System::Call 'Shell32::SHChangeNotify(i ${SHCNE_ASSOCCHANGED}, i ${SHCNF_IDLIST}, i 0, i 0)'
;FunctionEnd

;------------------------------- End Installer --------------------------------


;----------------------------- Start Uninstaller ------------------------------

Function un.onInit
  MessageBox MB_ICONQUESTION|MB_YESNO|MB_DEFBUTTON2 "Are you sure you want to completely remove $(^Name) and all of its components?" IDYES +2
  Abort
FunctionEnd

Section Uninstall
  ; Unassociate all file types

;  System::Call 'Shell32::SHChangeNotify(i ${SHCNE_ASSOCCHANGED}, i ${SHCNF_IDLIST}, i 0, i 0)'

  ; Remove all Files
  RmDir /r "$INSTDIR\"

  ; Remove all shortcuts
  Delete "$SMPROGRAMS\Editra\Uninstall.lnk"
  Delete "$SMPROGRAMS\Editra\Website.lnk"
  Delete "$DESKTOP\Editra.lnk"
  Delete "$SMPROGRAMS\Editra\Editra.lnk"
  RMDir "$SMPROGRAMS\Editra"

  ; Cleanup Registry
  DeleteRegKey ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}"
  DeleteRegKey HKLM "${PRODUCT_DIR_REGKEY}"

  SetAutoClose true
SectionEnd

Function un.onUninstSuccess
  HideWindow
  MessageBox MB_ICONINFORMATION|MB_OK "$(^Name) was successfully removed from your computer."
FunctionEnd

;------------------------------ End Uninstaller -------------------------------
