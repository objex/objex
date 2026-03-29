# Open Objex 
## MCP Server

```text
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@+..-@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@-. .-@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@%:. .-@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@%:. .-@@@@@@@@@@@@@@@@@%#%@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@%:. .-@@@@@@@@@@@@@@@%+++++%@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@%:. .-@@@@@@@@@@@@@@@#+++++#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@%:. .-@@@@@@@@@@@@@@@@#*+*#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@%%%%@@@@@@@@@%:. .-@@@%####%@@@@@@@@@@@@@@@@@@@%##*#%@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@#*+++++++++#%@@@@%:. .-%=:..   ..-#@@@@:...-%@@@#-..     .:=#%-....=%@@@@@@@@@=....-%@@@@@
@@@@@@@@#++++++++++++++*%@@%:. ...  ....    .-#@@:   -%@#:.   ....    .-%*.   .#@@@@@@#:.  .+@@@@@@@
@@@@@@%*+++++++++++++++++#@%:.   .-*%@@@#-.   :#@:   -%*:.  .=#@@@%+.. .-%%-.  .=@@@@+..  :%@@@@@@@@
@@@@@@*+++++++++++++++++++%%:.  :*@@@@@@@@*.   :%:   -#-   .#@@@@@@@#.  .=@@+..  :#%-.  .+@@@@@@@@@@
@@@@@#++++++++++++++++++++*#:. .=@@@@@@@@@@+.  .*:   -+.   ...........  .-@@@#-.  ..   :#@@@@@@@@@@@
@@@@@#+++++++++++++++++++++#:. .*@@@@@@@@@@#.   +:   -=.                 -%@@@@+.    .=@@@@@@@@@@@@@
@@@@@#++++++++++++++++++++*#:. .=@@@@@@@@@@*.  .*:   -+.   =%%%%%%%%%%%%%%@@@@@*.    .=@@@@@@@@@@@@@
@@@@@%*+++++++++++++++++++%%:. .:#@@@@@@@@#:   :%:   -*-   .%@@@@@@@@*.=#@@@@%-.  ..   :#@@@@@@@@@@@
@@@@@@%++++++++++++++++++#@%:.  ..+%@@@@%+.   .#@:   -%*.   .+%@@@@#-.  .-@@*:.  .*#-.  .+@@@@@@@@@@
@@@@@@@@*+++++++++++++++%@@%:. ... ..::..   .:#@@:   -%@*:.   ..:...   .+@%=.   -%@@@+.   :#@@@@@@@@
@@@@@@@@@%#++++++++++*%@@@@%:...-*-..    ..:*@@@@:   -%@@@*:.       .:+%@#:....+@@@@@@#:....+@@@@@@@
@@@@@@@@@@@@@%%##%%@@@@@@@@@@@@@@@@@#****#@@@@@@@:   -%@@@@@@#*****#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@:   -%@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@:   -%@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@:  .-%@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@:  .=@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@:.:*@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
```

```bash
curl -fsSL https://raw.githubusercontent.com/objex/objex/main/scripts/install.sh | bash
```

Turn messy enterprise APIs into an MCP-friendly toolbox with one command, a little scanning, and a lot less yak shaving.

## Contributors

Objex is for builders who enjoy making hard systems feel easy.

If you want to help, you are in the right place. The project is early, ambitious, and wide open for sharp contributions in the fun parts:

- MCP server architecture
- API discovery and normalization
- Gemini CLI integration
- OpenAPI generation quality
- enterprise auth and policy controls
- developer experience and installation flow

Quick start for local development:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
objex --help
```

Core commands:

- `objex install`
- `objex scan`
- `objex update`
- `objex list`

Local state lives in `~/.objex/<username>/`.

Project direction lives in [goals.md](/Users/mazhar/rabbito/objex/goals.md).

## What It Does

Objex is an open source MCP server and CLI that uses Gemini CLI to discover APIs across an enterprise and make them accessible through Objex.

The mission is simple: stop forcing every team and every agent to rediscover the same internal APIs from scratch.

## Why It Exists

Most enterprises already have a jungle of:

- internal REST services
- half-documented partner integrations
- API gateways with mystery endpoints
- repos that quietly contain useful routes nobody wrote down
- AI agents that could help, if only they knew what tools existed

Objex scans codebases and enterprise sources, builds a usable inventory, and turns that inventory into MCP-friendly access.

## How It Works

1. `objex install` registers a user profile with the Objex API.
2. `objex scan` inspects a codebase for likely REST operations.
3. Objex generates an OpenAPI 3 spec from the discovered routes.
4. The spec is stored locally and uploaded to the Objex API.
5. The broader Objex platform can then expose those capabilities through MCP.

## Install Options

### One-Line Install

```bash
curl -fsSL https://raw.githubusercontent.com/objex/objex/main/scripts/install.sh | bash
```

### macOS with Homebrew

```bash
brew install --HEAD ./Formula/objex.rb
```

The formula lives at [Formula/objex.rb](/Users/mazhar/rabbito/objex/Formula/objex.rb).

### Linux or Manual Python Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
objex --help
```

## Current Shape

Today the CLI can:

- register users against `https://api.objex.app/mcp`
- store local profiles
- scan Python and JavaScript codebases for common REST route patterns
- generate OpenAPI 3.0 specs
- upload discovered codebase specs back to Objex

This is an early foundation, not the finished cathedral.

## Repo Layout

- [objex_cli/cli.py](/Users/mazhar/rabbito/objex/objex_cli/cli.py) contains the command entry points
- [objex_cli/scanner.py](/Users/mazhar/rabbito/objex/objex_cli/scanner.py) contains route detection and OpenAPI generation
- [objex_cli/api.py](/Users/mazhar/rabbito/objex/objex_cli/api.py) contains Objex API calls
- [objex_cli/storage.py](/Users/mazhar/rabbito/objex/objex_cli/storage.py) manages local state
- [scripts/install.sh](/Users/mazhar/rabbito/objex/scripts/install.sh) installs the CLI

## License

Apache 2.0. See [LICENSE](/Users/mazhar/rabbito/objex/LICENSE).
