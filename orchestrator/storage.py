import asyncio
from schemas.agent_artifacts import MCPArtifact

class DBManager:
    @staticmethod
    async def save_artifact(artifact: MCPArtifact):
        # Simulate blocking I/O for 0.5 seconds
        await asyncio.sleep(0.5)
        print(f"Saved artifact: {artifact.artifact_id}")
