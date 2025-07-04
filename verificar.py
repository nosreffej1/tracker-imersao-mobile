
print("="*50)
print("VERIFICANDO COMPONENTES 'PICKER' KIVYMD INSTALADOS")
print("="*50)

try:
    
    import kivymd.uix.dialog as dialogs
    print("\n--- Componentes Disponíveis em 'kivymd.uix.dialog' ---")
    
    
    count = 0
    for item in dir(dialogs):
        if "Picker" in item or "Dialog" in item:
            print(f"  - {item}")
            count += 1
    
    if count == 0:
        print("  Nenhum componente 'Picker' ou 'Dialog' encontrado.")

except ImportError:
    print("\nNão foi possível importar 'kivymd.uix.dialog'. Tentando caminho antigo...")
    try:
        import kivymd.uix.pickers as pickers
        print("\n--- Componentes Disponíveis em 'kivymd.uix.pickers' (caminho antigo) ---")
        for item in dir(pickers):
            if item.startswith('MD'):
                print(f"  - {item}")
    except ImportError:
        print("\nNão foi possível importar 'kivymd.uix.pickers'.")


print("\n" + "="*50)
print("Verificação concluída.")
print("="*50)
