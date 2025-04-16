#!/usr/bin/env python3
"""
Script to run the HypnoBot API server.
"""
import uvicorn
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run the HypnoBot API server')
    parser.add_argument('--host', type=str, default='127.0.0.1', help='Host to run the server on')
    parser.add_argument('--port', type=int, default=8000, help='Port to run the server on')
    parser.add_argument('--reload', action='store_true', help='Enable auto-reload for development')
    
    args = parser.parse_args()
    
    print(f"Starting HypnoBot API server at http://{args.host}:{args.port}")
    print("API documentation available at /docs")
    
    uvicorn.run("src.hypnobot.api:app", 
                host=args.host, 
                port=args.port, 
                reload=args.reload) 