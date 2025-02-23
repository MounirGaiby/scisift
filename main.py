import argparse
from cli_app import run_cli
from gui_app import run_gui

def main():
    parser = argparse.ArgumentParser(description='SciSift - Scientific Paper Analysis Tool')
    parser.add_argument('--gui', action='store_true', help='Run in GUI mode (default: CLI mode)')
    args = parser.parse_args()
    
    if args.gui:
        run_gui()
    else:
        run_cli()

if __name__ == "__main__":
    main()