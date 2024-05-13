FROM public.ecr.aws/lambda/python:3.9

ARG APP_PATH=lambda_handler.py
ARG SCRIPTS_PATH=scripts/spotify.py
COPY ${APP_PATH} ${LAMBDA_TASK_ROOT} 
COPY ${SCRIPTS_PATH} ${LAMBDA_TASK_ROOT} 

CMD [ "lambda_handler.lambda_handler" ]