from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from models.base import SessionLocal
from models.user import User, Whitelist
from services.docker_manager import DockerManager
from core.security import get_current_user, is_admin
from schemas.token import TokenData
from schemas.minecraft import WhitelistAdd, WhitelistRemove
import subprocess
import os
import time

router = APIRouter(prefix="/minecraft", tags=["minecraft"])

# Track server status
minecraft_server = {
    "running": False,
    "pid": None,
    "start_time": None
}

@router.post("/start")
async def start_server():
    """Start the Minecraft server"""
    if minecraft_server["running"]:
        raise HTTPException(status_code=400, detail="Server is already running")
    
    try:
        # Start Minecraft server
        process = subprocess.Popen(
            ["java", "-Xmx1024M", "-Xms1024M", "-jar", "server.jar", "nogui"],
            cwd="/minecraft",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        minecraft_server.update({
            "running": True,
            "pid": process.pid,
            "start_time": time.time()
        })
        
        return {"status": "started", "pid": process.pid}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stop")
async def stop_server():
    """Stop the Minecraft server"""
    if not minecraft_server["running"]:
        raise HTTPException(status_code=400, detail="Server is not running")
    
    try:
        # Stop Minecraft server
        os.kill(minecraft_server["pid"], 9)
        minecraft_server.update({
            "running": False,
            "pid": None,
            "start_time": None
        })
        return {"status": "stopped"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/server-stats")
async def get_server_stats():
    """Get Minecraft server statistics"""
    if not minecraft_server["running"]:
        raise HTTPException(status_code=400, detail="Server is not running")
    
    uptime = time.time() - minecraft_server["start_time"]
    return {
        "status": "running",
        "uptime": uptime,
        "pid": minecraft_server["pid"]
    }
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/start-afk")
async def start_afk_session(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    current_user = get_current_user(token, db)
    
    # Check if user is whitelisted
    whitelist = db.query(Whitelist).filter(Whitelist.ign == current_user.ign).first()
    if not whitelist or not whitelist.approved:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account is not whitelisted"
        )

    docker_manager = DockerManager()
    try:
        container = docker_manager.start_minecraft_client(current_user, db)
        return {"status": "success", "container_id": container.id}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/stop-afk")
async def stop_afk_session(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    current_user = get_current_user(token, db)
    docker_manager = DockerManager()
    success = docker_manager.stop_minecraft_client(current_user.ign)
    return {"status": "success" if success else "not_running"}

@router.get("/status")
async def get_afk_status(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    current_user = get_current_user(token, db)
    docker_manager = DockerManager()
    status = docker_manager.check_client_status(current_user.ign)
    return status

@router.get("/stats")
async def get_afk_stats(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    current_user = get_current_user(token, db)
    docker_manager = DockerManager()
    status = docker_manager.check_client_status(current_user.ign)
    
    if not status['stats']:
        return {
            "items_collected": 0,
            "shiny_items": 0,
            "session_time": 0,
            "cpu_usage": 0,
            "memory_usage": 0
        }
        
    return {
        "items_collected": 0,  # TODO: Implement item tracking
        "shiny_items": 0,      # TODO: Implement shiny tracking
        "session_time": status['stats']['session_time'],
        "cpu_usage": status['stats']['cpu_usage'],
        "memory_usage": status['stats']['memory_usage']
    }

@router.post("/whitelist/add")
async def add_to_whitelist(
    whitelist_data: WhitelistAdd,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """Add a player to the whitelist (admin only)"""
    current_user = get_current_user(token, db)
    if not is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can manage whitelist"
        )

    # Check if already whitelisted
    existing = db.query(Whitelist).filter(Whitelist.ign == whitelist_data.ign).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Player is already whitelisted"
        )

    new_entry = Whitelist(
        ign=whitelist_data.ign,
        approved=True,
        added_by=current_user.id
    )
    db.add(new_entry)
    db.commit()
    
    return {"status": "success", "message": f"Added {whitelist_data.ign} to whitelist"}

@router.post("/whitelist/remove")
async def remove_from_whitelist(
    whitelist_data: WhitelistRemove,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """Remove a player from the whitelist (admin only)"""
    current_user = get_current_user(token, db)
    if not is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can manage whitelist"
        )

    entry = db.query(Whitelist).filter(Whitelist.ign == whitelist_data.ign).first()
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found in whitelist"
        )

    db.delete(entry)
    db.commit()
    
    return {"status": "success", "message": f"Removed {whitelist_data.ign} from whitelist"}

@router.get("/whitelist")
async def get_whitelist(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """Get current whitelist (admin only)"""
    current_user = get_current_user(token, db)
    if not is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can view whitelist"
        )

    whitelist = db.query(Whitelist).all()
    return [{"ign": w.ign, "approved": w.approved} for w in whitelist]
