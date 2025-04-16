# HypnoBot package initialization 

# Apply memory patch to avoid embedchain dependency issues
try:
    from .memory_patch import patch_memory
    patch_memory()
    print("📦 Applied memory patch at hypnobot package level")
except Exception as e:
    print(f"⚠️ Warning: Failed to apply memory patch at package level: {e}")

# Package initialization 