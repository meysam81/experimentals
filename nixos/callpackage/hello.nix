{ writeShellScriptBin, audience ? "world" }:
writeShellScriptBin "hello" ''
  echo "hello ${audience}"
''

