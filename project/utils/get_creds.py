import os


def get_dataset_creds(dataset: str) -> tuple:
    match dataset:
        case "ftth":
            return os.environ["NEO_FTTH_URI"], os.environ["NEO_FTTH_USER"], os.environ["NEO_FTTH_PASS"]
        case "hospital":
            return os.environ["NEO_HOSPITAL_URI"], os.environ["NEO_HOSPITAL_USER"], os.environ["NEO_HOSPITAL_PASS"]
        case "ecommerce":
            return os.environ["NEO_ECOM_URI"], os.environ["NEO_ECOM_USER"], os.environ["NEO_ECOM_PASS"]
        case _:
            raise Exception(f"Dataset not supported")