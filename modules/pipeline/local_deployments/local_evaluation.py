from sagemaker.local import LocalSession
from sagemaker.processing import ProcessingInput, ProcessingOutput
from sagemaker.sklearn.processing import SKLearnProcessor

# Adapted from: https://github.com/aws-samples/amazon-sagemaker-local-mode/blob/main/scikit_learn_local_processing/SKLearnProcessor_local_processing.py
sagemaker_session = LocalSession()
sagemaker_session.config = {'local': {'local_code': True}}

# Configure local execution parameters
INSPECT_AFTER_SCRIPT = True
CODE_PATH = "../../../src/mlmax/evaluation.py"
LOCAL_DATA_PATH = "../../../tests/mlmax/opt/ml/processing/test"
EXECUTION_MODE = "infer"  # Configure to either 'train', or 'infer'

# For local training a dummy role will be sufficient
role = 'arn:aws:iam::111111111111:role/service-role/AmazonSageMaker-ExecutionRole-20200101T000001'
if INSPECT_AFTER_SCRIPT:
    command = ["python3", "-i", "/opt/ml/processing/input/code/evaluation.py"]
else:
    command = ["python3", "/opt/ml/processing/input/code/evaluation.py"]
processor = SKLearnProcessor(framework_version='0.20.0',
                             instance_count=1,
                             instance_type='local',
                             role=role,
                             max_runtime_in_seconds=1200,
                             command=command
                             )

print('Starting processing job.')
print('Note: if launching for the first time in local mode, container image download might take a few minutes to complete.')
processor.run(
    code=CODE_PATH,
    inputs=[
        ProcessingInput(
            source=LOCAL_DATA_PATH,
            destination="/opt/ml/processing/test",
            input_name="input",
        ),
        ProcessingInput(
            source="../../../tests/mlmax/opt/ml/processing/model",
            destination="/opt/ml/processing/model",
            input_name="model",
        ),
    ],
    outputs=[
        ProcessingOutput(
            source="/opt/ml/processing/evaluation",
            output_name="evaluation",
        )
    ],
    wait=False
)

evaluation_job_description = processor.jobs[-1].describe()
output_config = evaluation_job_description['ProcessingOutputConfig']
print(output_config)

for output in output_config['Outputs']:
    if output['OutputName'] == 'evaluation':
        output_data_file = output['S3Output']['S3Uri']

print('Output file is located on: {}'.format(output_data_file))
