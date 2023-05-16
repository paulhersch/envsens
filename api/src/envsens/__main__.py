import uvicorn
import argparse

argparser = argparse.ArgumentParser(
    prog='Envsens API'
)
argparser.add_argument('--port',
                       help='The port the uvicorn server should run on',
                       default=8080,
                       type=int)
args = argparser.parse_args()

uvicorn.run("app:app", host='0.0.0.0', port=args.port, log_level="info", reload=True)
