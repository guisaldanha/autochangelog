; Inno Setup script for AutoChangelog.
; Builds a Windows installer around the PyInstaller output (dist\autochangelog.exe)
; and adds the install directory to PATH, so `autochangelog` works from any terminal
; without the user having to touch environment variables by hand.
;
; Keep MyAppVersion in sync with _version.py on each release.

#define MyAppName "AutoChangelog"
#define MyAppVersion "2.0.1"
#define MyAppPublisher "Guilherme Saldanha"
#define MyAppURL "https://github.com/guisaldanha/autochangelog"
#define MyAppExeName "autochangelog.exe"

[Setup]
AppId={{5C6C9C3E-2C0E-4C2E-9E4E-9F8B1C2A6D3F}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
DisableProgramGroupPage=yes
LicenseFile=..\LICENSE
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
OutputDir=..\dist
OutputBaseFilename=AutoChangelogSetup{#MyAppVersion}
Compression=lzma
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\{#MyAppExeName}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Tasks]
Name: "addtopath"; Description: "Add {#MyAppName} to the PATH environment variable (recommended)"; GroupDescription: "Additional options:"; Flags: checkedonce

[Files]
Source: "..\dist\autochangelog.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\LICENSE"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; A CLI tool has no window of its own to launch, so the shortcut opens a
; terminal with --help already run, which both proves PATH works and shows
; the user how to use the command.
Name: "{autoprograms}\{#MyAppName}"; Filename: "{cmd}"; Parameters: "/K ""{app}\{#MyAppExeName}"" --help"; WorkingDir: "{app}"; IconFilename: "{app}\{#MyAppExeName}"

[UninstallDelete]
Type: filesandordirs; Name: "{app}"

[Code]
const
  ENV_HWND_BROADCAST = $FFFF;
  ENV_WM_SETTINGCHANGE = $1A;
  ENV_SMTO_ABORTIFHUNG = $0002;

function SendMessageTimeoutA(hWnd: Longint; Msg: Longint; wParam: Longint; lParam: string;
  fuFlags, uTimeout: Longint; var lpdwResult: Longint): Longint;
  external 'SendMessageTimeoutA@user32.dll stdcall';

function EnvRootKey: Integer;
begin
  if IsAdminInstallMode then
    Result := HKLM
  else
    Result := HKCU;
end;

function EnvSubkey: string;
begin
  if IsAdminInstallMode then
    Result := 'SYSTEM\CurrentControlSet\Control\Session Manager\Environment'
  else
    Result := 'Environment';
end;

procedure RefreshEnvironment;
var
  ResultCode: Longint;
begin
  SendMessageTimeoutA(ENV_HWND_BROADCAST, ENV_WM_SETTINGCHANGE, 0, 'Environment', ENV_SMTO_ABORTIFHUNG, 5000, ResultCode);
end;

procedure AddAppToPath;
var
  OrigPath, NewPath, AppDir: string;
begin
  AppDir := ExpandConstant('{app}');

  if not RegQueryStringValue(EnvRootKey, EnvSubkey, 'Path', OrigPath) then
    OrigPath := '';

  { Already present? Nothing to do (comparison is case-insensitive, like Windows paths). }
  if Pos(';' + Uppercase(AppDir) + ';', ';' + Uppercase(OrigPath) + ';') > 0 then
    Exit;

  if (OrigPath <> '') and (OrigPath[Length(OrigPath)] <> ';') then
    NewPath := OrigPath + ';' + AppDir
  else
    NewPath := OrigPath + AppDir;

  RegWriteExpandStringValue(EnvRootKey, EnvSubkey, 'Path', NewPath);
  RefreshEnvironment;
end;

procedure RemoveAppFromPath;
var
  OrigPath, AppDir: string;
  Parts: TStringList;
  I: Integer;
begin
  if not RegQueryStringValue(EnvRootKey, EnvSubkey, 'Path', OrigPath) then
    Exit;

  AppDir := ExpandConstant('{app}');
  Parts := TStringList.Create;
  try
    Parts.Delimiter := ';';
    Parts.StrictDelimiter := True;
    Parts.DelimitedText := OrigPath;
    for I := Parts.Count - 1 downto 0 do
    begin
      if CompareText(Parts[I], AppDir) = 0 then
        Parts.Delete(I);
    end;
    RegWriteExpandStringValue(EnvRootKey, EnvSubkey, 'Path', Parts.DelimitedText);
  finally
    Parts.Free;
  end;
  RefreshEnvironment;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if (CurStep = ssPostInstall) and WizardIsTaskSelected('addtopath') then
    AddAppToPath;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  if CurUninstallStep = usPostUninstall then
    RemoveAppFromPath;
end;
