FROM public.ecr.aws/lambda/python:3.9

ARG APP_PATH=lambda_handler.py
ARG REQ_PATH=requirements.txt
ARG SCRIPTS_PATH=scripts/
COPY ${APP_PATH} ${LAMBDA_TASK_ROOT} 
COPY ${SCRIPTS_PATH} ${LAMBDA_TASK_ROOT}/scripts/ 
COPY ${REQ_PATH} ${LAMBDA_TASK_ROOT}
WORKDIR ${LAMBDA_TASK_ROOT}
RUN pip install -r requirements.txt
CMD [ "lambda_handler.lambda_handler" ]
