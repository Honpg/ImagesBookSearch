import httpx
import numpy as np
import torch
import torch.nn as nn

class TritonClient:
    def __init__(self, server_url="http://triton-server:8000"):
        self.server_url = server_url

    def call_triton_inference(self, model_name, input_tensor):
        """Gọi Triton Server để thực hiện inference và nhận kết quả (đồng bộ)."""
        if input_tensor is None or not isinstance(input_tensor, np.ndarray):
            raise ValueError("input_tensor phải là một numpy array hợp lệ.")

        payload = {
            "inputs": [
                {
                    "name": "input__0",
                    "shape": list(input_tensor.shape),
                    "datatype": "FP32",
                    "data": input_tensor.flatten().tolist()
                }
            ],
            "outputs": [{"name": "output__0"}]
        }

        try:
            with httpx.Client(timeout=10.0) as client:  
                response = client.post(
                    f"{self.server_url}/v2/models/{model_name}/infer", 
                    json=payload
                )
            
            if response.status_code != 200:
                raise Exception(f"Lỗi từ Triton Server: {response.status_code} - {response.text}")

            result = response.json()

            if "outputs" not in result or len(result["outputs"]) == 0:
                raise ValueError("Kết quả trả về từ Triton không hợp lệ.")
            
            output_tensor = np.array(result["outputs"][0]["data"])
            return output_tensor

        except httpx.RequestError as e:
            raise ConnectionError(f"Lỗi kết nối tới Triton Server: {str(e)}")
        except ValueError as ve:
            raise ValueError(f"Lỗi dữ liệu: {str(ve)}")
        except Exception as ex:
            raise RuntimeError(f"Lỗi không xác định: {str(ex)}")
