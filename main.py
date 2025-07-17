from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
import uvicorn
import time
import logging
import os
from dotenv import load_dotenv

# Import routers
import auth
import users
import musteriler

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PerformanceMiddleware(BaseHTTPMiddleware):
    """Middleware to track request performance"""
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        process_time = time.time() - start_time
        
        # Log performance metrics
        logger.info(
            f"Path: {request.url.path} | "
            f"Method: {request.method} | "
            f"Duration: {process_time:.3f}s | "
            f"Status: {response.status_code}"
        )
        
        # Add performance header
        response.headers["X-Process-Time"] = str(process_time)
        
        # Alert on slow requests (>1 second)
        if process_time > 1.0:
            logger.warning(
                f"Slow request detected: {request.url.path} took {process_time:.3f}s"
            )
        
        return response

# Create FastAPI app with optimized configuration
app = FastAPI(
    title="Customer Management API",
    description="Optimized FastAPI application for customer management",
    version="1.0.0",
    docs_url="/docs" if os.getenv("ENVIRONMENT") != "production" else None,
    redoc_url="/redoc" if os.getenv("ENVIRONMENT") != "production" else None,
    openapi_url="/openapi.json" if os.getenv("ENVIRONMENT") != "production" else None
)

# Add performance middleware
app.add_middleware(PerformanceMiddleware)

# Add GZIP compression for responses > 1KB
app.add_middleware(GZipMiddleware, minimum_size=1000)

# CORS middleware with security considerations
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(musteriler.router)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Customer Management API",
        "status": "healthy",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Detailed health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "environment": os.getenv("ENVIRONMENT", "development")
    }

if __name__ == "__main__":
    # Determine number of workers based on CPU count
    import multiprocessing
    workers = int(os.getenv("WORKERS", multiprocessing.cpu_count()))
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        workers=workers if os.getenv("ENVIRONMENT") == "production" else 1,
        loop="uvloop",  # Use uvloop for better performance
        http="httptools",  # Use httptools for better HTTP performance
        reload=os.getenv("ENVIRONMENT") != "production",  # Only reload in development
        log_level="info"
    )