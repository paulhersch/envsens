import uvicorn
import argparse


def main():
    argparser = argparse.ArgumentParser(
        prog='Envsens API'
    )
    argparser.add_argument('--port',
                           help='The port the uvicorn server should run on',
                           default=8888,
                           type=int)
    argparser.add_argument('--verbosity',
                           help='Verbosity of the API on cmdline',
                           default='warning',
                           choices=[
                               'info',
                               'warning',
                               'error'
                           ])
    args = argparser.parse_args()

    uvicorn.run("envsens.app:app", host='0.0.0.0', port=args.port, log_level=args.verbosity)


if __name__ == "__main__":
    main()
