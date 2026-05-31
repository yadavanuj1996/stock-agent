import docker
import tempfile
import os

# connect to local Docker daemon
client = docker.from_env()

def execute_code(code: str, csv_data: str = None, sp500_csv_data: str = None, csv_1y_data: str = None) -> dict:

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        temp_file = f.name

    output_dir = tempfile.mkdtemp()
    csv_file = None
    sp500_csv_file = None
    csv_1y_file = None

    if csv_data:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_data)
            csv_file = f.name

    if sp500_csv_data:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(sp500_csv_data)
            sp500_csv_file = f.name

    if csv_1y_data:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_1y_data)
            csv_1y_file = f.name

    container = None

    try:
        volumes = {
            temp_file: {"bind": "/code/script.py", "mode": "ro"},
            output_dir: {"bind": "/output", "mode": "rw"},
        }

        if csv_file:
            volumes[csv_file] = {"bind": "/data/stock_data.csv", "mode": "ro"}

        if sp500_csv_file:
            volumes[sp500_csv_file] = {"bind": "/data/sp500_data.csv", "mode": "ro"}

        if csv_1y_file:
            volumes[csv_1y_file] = {"bind": "/data/stock_data_1y.csv", "mode": "ro"}

        container = client.containers.run(
            image="stock-sandbox",
            command="python /code/script.py",
            volumes=volumes,
            mem_limit="512m",
            network_disabled=True,
            detach=True,
            stdout=True,
            stderr=True,
        )

        result = container.wait(timeout=30)
        output = container.logs().decode("utf-8")
        container.remove()
        container = None

        charts = []
        for file in os.listdir(output_dir):
            if file.endswith(".png"):
                charts.append(os.path.join(output_dir, file))

        return {
            "success": True,
            "output": output,
            "charts": charts,
            "error": None
        }

    except Exception as e:
        if container:
            try:
                container.kill()
                container.remove()
            except Exception:
                pass
        return {
            "success": False,
            "output": None,
            "charts": [],
            "error": str(e)
        }

    finally:
        os.unlink(temp_file)
        if csv_file:
            os.unlink(csv_file)
        if sp500_csv_file:
            os.unlink(sp500_csv_file)
        if csv_1y_file:
            os.unlink(csv_1y_file)
        if not os.listdir(output_dir):
            os.rmdir(output_dir)
