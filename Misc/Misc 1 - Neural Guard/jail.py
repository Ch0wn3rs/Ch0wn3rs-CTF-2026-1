#!/usr/bin/python3
import sys
import builtins

def main():
    print(" === Neural Guard - Expresión de Verificación AI ===")
    print("Ingresa tu expresión matemática para ser evaluada por la red.")
    print("Nota: Por seguridad, se han desactivado los métodos sensibles.")
    print("El Guardián Neural está observando...")
    
    while True:
        try:
            print(">>> ", end="", flush=True)
            user_input = sys.stdin.readline().strip()
            
            if not user_input:
                break

            # Filtro de seguridad (Dificultad Media)
            # Bloqueamos cadenas literales peligrosas
            blacklist = ['os', 'system', 'flag', 'import', 'eval', 'exec', 'subprocess', 'sh', 'getattr', 'chr']
            
            dangerous = False
            user_input_lower = user_input.lower()
            for word in blacklist:
                if word in user_input_lower:
                    print(f"Alerta: El Guardián Neural ha detectado la palabra prohibida: '{word}'", flush=True)
                    dangerous = True
                    break
            
            if dangerous:
                continue
            
            # Entorno controlado pero con acceso a builtins para permitir bypasses de nivel medio
            safe_env = {
                '__builtins__': builtins.__dict__
            }
            
            result = eval(user_input, safe_env, {})
            print(f"Resultado: {result}", flush=True)
            
        except Exception as e:
            print(f"Error: {e}", flush=True)

if __name__ == "__main__":
    main()
