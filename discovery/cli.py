import click
from datetime import datetime
from pathlib import Path
from discovery.settings import get_settings

settings = get_settings()


@click.group()
def cli():
    pass


@cli.command()
@click.option(
    "--target-path",
    default=settings.extract_target_folder_path,
    help="The folder path to save the data snapshot",
)
def extract(target_path: str):
    """
    Extract data from all various sources and save it to a target
    """

    click.echo("Extracting data from Azure Resource Graph")

    try:
        from azure.identity import DefaultAzureCredential
        from discovery.sources.azure_arm import AzureARM
        from discovery.repository import MemoryRepository

        credential = DefaultAzureCredential()
        repository = MemoryRepository()
        azure_arm = AzureARM(credential, repository)
        azure_arm.extract_all_resources()

        from discovery.repository.targets import SQLiteTarget

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        db_path = Path(Path(target_path) / f"extract_{timestamp}.db")
        target = SQLiteTarget(db_path)
        repository.save_to(target)
    except Exception as e:
        click.echo(f"Error: {e}")
        raise click.Abort()


@cli.command()
@click.option(
    "--target-path",
    default=settings.extract_target_folder_path,
    help="The folder path to get the latest data snapshot from",
)
@click.option("--query", help="The user task to run on AI agents")
def run(target_path: str, query: str):
    def get_azure_openai_model():
        """
        TODO: Provide possibility to switch between different models with command line arguments
        """
        from smolagents import AzureOpenAIServerModel

        return AzureOpenAIServerModel(
            model_id=settings.azure_openai_deployment_name,
            azure_endpoint=settings.azure_openai_endpoint,
            api_key=settings.azure_openai_key,
            api_version=settings.azure_openai_api_version
        )

    from discovery.agents import get_sqlite_agent

    agent = get_sqlite_agent(model = get_azure_openai_model())

    agent.run(query, additional_args={"target_path": target_path})


if __name__ == "__main__":
    cli()
