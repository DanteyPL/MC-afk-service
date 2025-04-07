import docker
from docker.errors import DockerException
from core.config import settings
from models.user import User
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)

class DockerManager:
    def __init__(self):
        try:
            self.client = docker.from_env()
            self.network_name = settings.DOCKER_NETWORK
            self.mc_image = settings.DOCKER_MC_IMAGE
            self._ensure_network_exists()
        except DockerException as e:
            logger.error(f"Failed to initialize Docker client: {e}")
            raise

    def _ensure_network_exists(self):
        """Ensure the Docker network exists"""
        try:
            networks = self.client.networks.list(names=[self.network_name])
            if not networks:
                self.client.networks.create(
                    self.network_name,
                    driver="bridge",
                    check_duplicate=True
                )
        except DockerException as e:
            logger.error(f"Failed to ensure network exists: {e}")
            raise

    def start_minecraft_client(self, user: User, db: Session):
        """Start a Minecraft client container for the user"""
        try:
            # Get decrypted Microsoft credentials
            ms_password = ""
            if user.store_password and user.encrypted_ms_credentials:
                from core.security import decrypt_data
                ms_password = decrypt_data(user.encrypted_ms_credentials)
                
            container = self.client.containers.run(
                image=self.mc_image,
                name=f"mc-client-{user.ign}",
                environment={
                    "MC_USERNAME": user.ign,
                    "MC_PASSWORD": ms_password,
                    "MC_SERVER": settings.MC_SERVER,
                    "MC_PORT": str(settings.MC_PORT),
                    "EULA": "TRUE"
                },
                network=self.network_name,
                detach=True,
                restart_policy={"Name": "unless-stopped"},
                volumes={
                    f"mc-data-{user.ign}": {
                        "bind": "/data",
                        "mode": "rw"
                    }
                }
            )
            logger.info(f"Started Minecraft client for {user.ign}")
            return container
        except DockerException as e:
            logger.error(f"Failed to start Minecraft client for {user.ign}: {e}")
            raise RuntimeError(f"Failed to start Minecraft client: {e}")

    def stop_minecraft_client(self, ign: str):
        """Stop and remove a Minecraft client container"""
        try:
            container = self.client.containers.get(f"mc-client-{ign}")
            container.stop()
            container.remove()
            logger.info(f"Stopped Minecraft client for {ign}")
            return True
        except DockerException as e:
            logger.warning(f"Failed to stop Minecraft client for {ign}: {e}")
            return False

    def check_client_status(self, ign: str):
        """Check the status of a Minecraft client container"""
        try:
            container = self.client.containers.get(f"mc-client-{ign}")
            stats = container.stats(stream=False)
            return {
                "status": container.status,
                "logs": container.logs(tail=10).decode('utf-8'),
                "stats": {
                    "cpu_usage": stats['cpu_stats']['cpu_usage']['total_usage'],
                    "memory_usage": stats['memory_stats']['usage'],
                    "session_time": (
                        stats['read'] - stats['precpu_stats']['system_cpu_usage']
                    ) / 1e9  # Convert nanoseconds to seconds
                }
            }
        except DockerException as e:
            logger.debug(f"Container for {ign} not found: {e}")
            return {
                "status": "not_running",
                "logs": "",
                "stats": None
            }

    def start_minecraft_server(self):
        """Start the Minecraft server container"""
        try:
            container = self.client.containers.run(
                image=self.mc_image,
                name="mc-server",
                environment={
                    "EULA": "TRUE",
                    "MEMORY": "1024M"
                },
                network=self.network_name,
                ports={'25565/tcp': 25565},
                detach=True,
                restart_policy={"Name": "unless-stopped"},
                volumes={
                    "mc-server-data": {
                        "bind": "/data",
                        "mode": "rw"
                    }
                }
            )
            logger.info("Started Minecraft server")
            return container
        except DockerException as e:
            logger.error(f"Failed to start Minecraft server: {e}")
            raise RuntimeError(f"Failed to start Minecraft server: {e}")

    def stop_minecraft_server(self):
        """Stop the Minecraft server container"""
        try:
            container = self.client.containers.get("mc-server")
            container.stop()
            container.remove()
            logger.info("Stopped Minecraft server")
            return True
        except DockerException as e:
            logger.warning(f"Failed to stop Minecraft server: {e}")
            return False

    def get_server_status(self):
        """Get the status of the Minecraft server container"""
        try:
            container = self.client.containers.get("mc-server")
            stats = container.stats(stream=False)
            return {
                "status": container.status,
                "uptime": (
                    stats['read'] - stats['precpu_stats']['system_cpu_usage']
                ) / 1e9,  # Convert nanoseconds to seconds
                "pid": container.id
            }
        except DockerException as e:
            logger.debug("Minecraft server container not found")
            return {
                "status": "not_running",
                "uptime": 0,
                "pid": None
            }
