"""
Script para limpiar archivos temporales y directorios generados por Great Expectations
"""
import os
import shutil

def cleanup():
    """Elimina archivos y directorios temporales"""
    items_to_remove = [
        'gx',  # Directorio de Great Expectations (File Context)
        'uncommitted',  # Directorio de datos no commiteados
        '.ipynb_checkpoints',  # Checkpoints de Jupyter
        'notebooks/.ipynb_checkpoints',
    ]
    
    print("Limpiando archivos temporales...")
    
    for item in items_to_remove:
        if os.path.exists(item):
            if os.path.isdir(item):
                try:
                    shutil.rmtree(item)
                    print(f"✓ Eliminado directorio: {item}")
                except Exception as e:
                    print(f"✗ Error al eliminar {item}: {e}")
            else:
                try:
                    os.remove(item)
                    print(f"✓ Eliminado archivo: {item}")
                except Exception as e:
                    print(f"✗ Error al eliminar {item}: {e}")
        else:
            print(f"- {item} no existe (ok)")
    
    print("\n¡Limpieza completada!")
    print("Nota: Los datasets en /data/ se mantienen intactos.")

if __name__ == "__main__":
    cleanup()
