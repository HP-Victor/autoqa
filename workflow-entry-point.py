import asyncio
import os
from agents import Agent, ModelSettings, Runner, function_tool
import re
import glob

MAX_TURNS = int(os.environ.get("MAX_TURNS", 100))
PROMPT = os.environ.get("PROMPT")

if not PROMPT:
    raise ValueError("PROMPT environment variable is not set")

# Elegir modelo desde variable de entorno
MODEL = os.environ.get("OPENAI_MODEL", "gpt-5-pro")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")

# Determinar si es modelo de Claude o OpenAI
if "claude" in MODEL.lower():
    if not ANTHROPIC_API_KEY:
        raise ValueError("Anthropic API key required for Claude models. Set ANTHROPIC_API_KEY")
    print(f"✅ Using Claude model for code generation: {MODEL}")
else:
    if not OPENAI_API_KEY:
        raise ValueError("OpenAI API key required for OpenAI models. Set OPENAI_API_KEY")
    print(f"✅ Using OpenAI model for code generation: {MODEL}")

# Herramientas para el agente


def analyze_existing_code(base_path):
    """Analiza COMPLETAMENTE el código existente en el repositorio objetivo"""
    analysis = {
        "page_objects": [],
        "test_classes": [],
        "utilities": [],
        "all_java_files": [],
        "structure": {}
    }
    
    if not os.path.exists(base_path):
        return analysis
    
    print(f"   🔍 Analizando TODOS los archivos Java en: {base_path}")
    
    # Buscar TODOS los archivos Java en el proyecto
    java_pattern = f"{base_path}/**/*.java"
    all_java_files = glob.glob(java_pattern, recursive=True)
    
    print(f"   📁 Encontrados {len(all_java_files)} archivos Java en total")
    
    for file_path in all_java_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                file_name = os.path.basename(file_path)
                relative_path = os.path.relpath(file_path, base_path)
                
                # Analizar el contenido para extraer métodos y clases importantes
                methods = extract_methods_from_java(content)
                class_name = extract_class_name_from_java(content)
                
                file_info = {
                    "file": file_path,
                    "name": file_name,
                    "relative_path": relative_path,
                    "class_name": class_name,
                    "methods": methods,
                    "content": content[:1000] + "..." if len(content) > 1000 else content
                }
                
                # Clasificar por tipo/ubicación
                if "/paginas/" in file_path or "Page" in file_name:
                    analysis["page_objects"].append(file_info)
                elif "/casos/" in file_path or "Test" in file_name:
                    analysis["test_classes"].append(file_info)
                elif "/utils/" in file_path or "Util" in file_name or "Helper" in file_name:
                    analysis["utilities"].append(file_info)
                
                # Agregar a la lista completa independientemente
                analysis["all_java_files"].append(file_info)
                
        except Exception as e:
            print(f"      ⚠️  Error leyendo {file_path}: {e}")
    
    print(f"   📊 Clasificación encontrada:")
    print(f"      - Page Objects: {len(analysis['page_objects'])}")
    print(f"      - Test Classes: {len(analysis['test_classes'])}")  
    print(f"      - Utilities: {len(analysis['utilities'])}")
    print(f"      - Otros archivos Java: {len(analysis['all_java_files']) - len(analysis['page_objects']) - len(analysis['test_classes']) - len(analysis['utilities'])}")
    
    return analysis

def extract_methods_from_java(java_content):
    """Extrae los nombres de métodos públicos de un archivo Java"""
    methods = []
    # Regex para capturar métodos públicos
    method_pattern = r'public\s+(?:static\s+)?(?:\w+\s+)*(\w+)\s*\([^)]*\)'
    matches = re.findall(method_pattern, java_content)
    return matches[:10]  # Limitar a 10 métodos principales

def extract_class_name_from_java(java_content):
    """Extrae el nombre de la clase principal de un archivo Java"""
    class_pattern = r'public\s+class\s+(\w+)'
    match = re.search(class_pattern, java_content)
    return match.group(1) if match else "Unknown"

def analyze_framework_libraries():
    """Analiza COMPLETAMENTE las librerías del framework para entender funciones disponibles"""
    framework_analysis = {
        "libraries": []
    }
    
    # Obtener paths de librerías desde variables de entorno (separadas por comas)
    framework_lib_paths = os.environ.get("FRAMEWORK_LIB_PATHS", "../selenium-driver-lib,../selenium-commons-lib")
    lib_paths = [path.strip() for path in framework_lib_paths.split(",") if path.strip()]
    
    for lib_path in lib_paths:
        if os.path.exists(lib_path):
            lib_name = os.path.basename(lib_path)
            print(f"   📚 Analizando librería {lib_name} en: {lib_path}")
            
            lib_analysis = {
                "name": lib_name,
                "path": lib_path,
                "classes": []
            }
            
            java_pattern = f"{lib_path}/**/*.java"
            java_files = glob.glob(java_pattern, recursive=True)
            print(f"      📁 Encontrados {len(java_files)} archivos Java en {lib_name}")
            
            for file_path in java_files:
                if file_path.endswith('.java'):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            class_name = extract_class_name_from_java(content)
                            methods = extract_methods_from_java(content)
                            relative_path = os.path.relpath(file_path, lib_path)
                            
                            lib_analysis["classes"].append({
                                "name": class_name,
                                "file_name": os.path.basename(file_path),
                                "relative_path": relative_path,
                                "methods": methods,
                                "file": file_path,
                                "content": content[:1200] + "..." if len(content) > 1200 else content
                            })
                    except Exception as e:
                        print(f"      ⚠️  Error leyendo {file_path}: {e}")
            
            framework_analysis["libraries"].append(lib_analysis)
            print(f"      ✅ {len(lib_analysis['classes'])} clases analizadas en {lib_name}")
            
            # Imprimir resumen de métodos encontrados
            total_methods = sum(len(cls.get('methods', [])) for cls in lib_analysis['classes'])
            print(f"      🔧 Total de métodos públicos encontrados: {total_methods}")
        else:
            print(f"   ⚠️  Librería no encontrada: {lib_path}")
    
    return framework_analysis

def analyze_additional_projects():
    """Analiza proyectos adicionales descargados para proporcionar contexto extra"""
    additional_projects = []
    
    # Obtener paths de proyectos adicionales desde variables de entorno
    additional_project_paths = os.environ.get("ADDITIONAL_PROJECT_PATHS", "")
    if not additional_project_paths:
        print("   ℹ️  No se especificaron proyectos adicionales (ADDITIONAL_PROJECT_PATHS vacío)")
        return additional_projects
    
    project_paths = [path.strip() for path in additional_project_paths.split(",") if path.strip()]
    if not project_paths:
        print("   ℹ️  No se encontraron paths válidos en ADDITIONAL_PROJECT_PATHS")
        return additional_projects
    
    for project_path in project_paths:
        if os.path.exists(project_path):
            project_name = os.path.basename(project_path)
            print(f"   📂 Analizando proyecto adicional: {project_name} en {project_path}")
            
            project_analysis = {
                "name": project_name,
                "path": project_path,
                "files": []
            }
            
            # Buscar archivos Java, XML, properties, etc.
            file_patterns = [
                "**/*.java",
                "**/*.xml", 
                "**/*.properties",
                "**/*.yml",
                "**/*.yaml",
                "**/README.md",
                "**/pom.xml"
            ]
            
            for pattern in file_patterns:
                full_pattern = f"{project_path}/{pattern}"
                for file_path in glob.glob(full_pattern, recursive=True):
                    try:
                        file_extension = os.path.splitext(file_path)[1][1:]  # Sin el punto
                        file_name = os.path.relpath(file_path, project_path)
                        
                        file_info = {
                            "name": file_name,
                            "type": file_extension or "file",
                            "path": file_path
                        }
                        
                        # Leer contenido para archivos importantes
                        if file_extension in ['java', 'xml', 'properties', 'md'] and os.path.getsize(file_path) < 5000:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                                file_info["content"] = content
                        
                        project_analysis["files"].append(file_info)
                        
                    except Exception as e:
                        print(f"      ⚠️  Error leyendo {file_path}: {e}")
            
            additional_projects.append(project_analysis)
            print(f"      📁 {len(project_analysis['files'])} archivos encontrados")
        else:
            print(f"   ⚠️  Proyecto adicional no encontrado: {project_path}")
    
    return additional_projects

def create_context_enhanced_prompt(original_prompt, code_analysis, framework_analysis, target_path, additional_projects=None):
    """Agrega contexto COMPLETO del código existente, librerías del framework y proyectos adicionales al prompt original"""
    context_addition = f"""

=== CONTEXTO AUTOMÁTICO AGREGADO POR AUTOQA ===

REPOSITORIO OBJETIVO PARA CREAR/EDITAR ARCHIVOS: {target_path}
=================================================================
IMPORTANTE: Cuando uses create_java_file() o replace_string_in_file(), las rutas deben comenzar con: {target_path}/

ANÁLISIS COMPLETO DEL PROYECTO OBJETIVO: {target_path}
=====================================================

TODOS LOS ARCHIVOS JAVA EXISTENTES ({len(code_analysis['all_java_files'])} archivos):

RESUMEN DE CLASES Y MÉTODOS DISPONIBLES:
"""
    
    # Crear un índice completo de clases y métodos
    for java_file in code_analysis['all_java_files']:
        context_addition += f"""
📁 {java_file['relative_path']}
   Clase: {java_file['class_name']}
   Métodos disponibles: {', '.join(java_file['methods']) if java_file['methods'] else 'Ninguno detectado'}
   
```java
{java_file['content']}
```
"""

    # Agregar análisis DETALLADO de las librerías del framework
    context_addition += f"""

LIBRERÍAS DEL FRAMEWORK DISPONIBLES:
=====================================
IMPORTANTE: Estas librerías ya contienen métodos implementados. NO DUPLICAR funcionalidad.

"""
    
    for lib in framework_analysis['libraries']:
        context_addition += f"""
🏗️ LIBRERÍA: {lib['name'].upper()} ({len(lib['classes'])} clases)
   Ubicación: {lib['path']}
   
   CLASES Y MÉTODOS DISPONIBLES:
"""
        for cls in lib['classes']:
            context_addition += f"""   
   📋 {cls['relative_path']} 
      Clase: {cls['name']}
      Métodos públicos: {', '.join(cls['methods']) if cls['methods'] else 'Ninguno detectado'}
      
   ```java
   {cls['content']}
   ```
   
"""
    
    # Agregar proyectos adicionales como contexto
    if additional_projects:
        context_addition += f"""
PROYECTOS DE REFERENCIA DESCARGADOS:
===================================
"""
        for project in additional_projects:
            context_addition += f"""
📂 {project['name'].upper()} - {project['path']}
   Archivos importantes:
"""
            for file_info in project['files'][:15]:  # Aumentar a 15 archivos
                context_addition += f"   - {file_info['name']}: {file_info['type']}\n"
                if file_info['type'] == 'java' and file_info.get('content'):
                    context_addition += f"""
```java
{file_info['content'][:600]}...
```
"""
    
    # Instrucciones específicas para evitar duplicación
    context_addition += f"""

🚨 INSTRUCCIONES CRÍTICAS PARA EVITAR DUPLICACIÓN:
=================================================
1. ANTES de crear cualquier método, REVISAR si ya existe en las librerías del framework
2. REUTILIZAR métodos existentes en lugar de crear nuevos
3. Si necesitas funcionalidad de esperas, acciones, o utilidades, USAR las clases del framework
4. Solo crear métodos nuevos si NO EXISTEN en el framework
5. Al usar métodos del framework, importar las clases correctamente

EJEMPLO DE REUTILIZACIÓN:
- Si necesitas esperar un elemento, usar métodos de las librerías de selenium
- Si necesitas realizar acciones, usar métodos de las librerías de acciones
- Si necesitas utilidades, usar métodos de las librerías de utils

"""
    
    # Combinar prompt original con contexto
    enhanced_prompt = f"{original_prompt}\n{context_addition}"
    
    return enhanced_prompt

# Configurar el directorio objetivo
TARGET_PROJECT_PATH = os.environ.get("TARGET_PROJECT_PATH", "../template-models")
print(f"🎯 Directorio objetivo configurado: {TARGET_PROJECT_PATH}")
print(f"🗂️  Directorio de trabajo actual: {os.getcwd()}")
print(f"🔍 ¿Existe el directorio objetivo?: {os.path.exists(TARGET_PROJECT_PATH)}")
if os.path.exists(TARGET_PROJECT_PATH):
    print(f"📁 Contenido del directorio objetivo: {os.listdir(TARGET_PROJECT_PATH)}")

# Analizar código existente
print(f"🔍 Analizando código existente en: {TARGET_PROJECT_PATH}")
code_analysis = analyze_existing_code(TARGET_PROJECT_PATH)
print(f"   📁 Page Objects encontrados: {len(code_analysis['page_objects'])}")
print(f"   📁 Tests encontrados: {len(code_analysis['test_classes'])}")
print(f"   📁 Utilidades encontradas: {len(code_analysis['utilities'])}")

# Analizar librerías del framework
print(f"🔍 Analizando librerías del framework...")
framework_analysis = analyze_framework_libraries()
for lib in framework_analysis['libraries']:
    print(f"   📚 Clases en {lib['name']}: {len(lib['classes'])}")

# Analizar proyectos adicionales para contexto
print(f"🔍 Analizando proyectos adicionales...")
additional_projects = analyze_additional_projects()
for project in additional_projects:
    print(f"   📂 Archivos en {project['name']}: {len(project['files'])}")

# Crear prompt con contexto del código existente, librerías del framework y proyectos adicionales
enhanced_prompt = create_context_enhanced_prompt(PROMPT, code_analysis, framework_analysis, TARGET_PROJECT_PATH, additional_projects)

# Herramientas del agente para trabajar con archivos
@function_tool
def create_java_file(file_path: str, content: str) -> str:
    """Crea un archivo Java en la ruta especificada con el contenido proporcionado"""
    try:
        # Crear directorio si no existe
        directory = os.path.dirname(file_path)
        os.makedirs(directory, exist_ok=True)
        
        # Escribir archivo
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Archivo Java creado: {file_path}")
        return f"Archivo creado exitosamente: {file_path}"
    except Exception as e:
        error_msg = f"Error creando archivo {file_path}: {e}"
        print(f"❌ {error_msg}")
        return error_msg

@function_tool
def read_file(file_path: str) -> str:
    """Lee el contenido de un archivo"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        print(f"📖 Archivo leído: {file_path}")
        return content
    except Exception as e:
        error_msg = f"Error leyendo archivo {file_path}: {e}"
        print(f"❌ {error_msg}")
        return error_msg

@function_tool
def replace_string_in_file(file_path: str, old_string: str, new_string: str) -> str:
    """Reemplaza una cadena en un archivo existente"""
    try:
        # Leer archivo
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar que el string existe
        if old_string not in content:
            return f"Error: La cadena especificada no se encontró en {file_path}"
        
        # Reemplazar
        new_content = content.replace(old_string, new_string)
        
        # Escribir archivo modificado
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✏️ Archivo modificado: {file_path}")
        return f"Reemplazo exitoso en: {file_path}"
    except Exception as e:
        error_msg = f"Error modificando archivo {file_path}: {e}"
        print(f"❌ {error_msg}")
        return error_msg

# Crear agente con herramientas de archivo
agent = Agent(
    model=MODEL,
    model_settings=ModelSettings(truncation="auto", reasoning={"summary": "auto"}),
    name="Code Generator and File Editor Agent",
    instructions=enhanced_prompt,
    tools=[create_java_file, read_file, replace_string_in_file]
)

# Función para extraer y crear archivos del código generado
# Funciones de extracción manual removidas - el agente crea archivos directamente

# Ejecutar agente
async def main():
    # El enhanced_prompt ya contiene:
    # 1. El PROMPT original del usuario (con su contexto y tarea)
    # 2. El contexto de FRAMEWORK_LIB_PATHS 
    # 3. El contexto de ADDITIONAL_PROJECT_PATHS
    
    result = Runner.run_streamed(agent, enhanced_prompt, max_turns=MAX_TURNS)

    async for event in result.stream_events():
        if hasattr(event, "type") and event.type == "raw_response_event":
            data = event.data
            if hasattr(data, "type") and data.type == "response.reasoning_summary_text.done":
                print(f"🧠 Agent reasoning: {data.text}")

    print(f"📝 Generated code output:\n{result.final_output}")
    print(f"✅ Ejecución completada. Los archivos fueron creados en: {TARGET_PROJECT_PATH}")

if __name__ == "__main__":
    print("Starting AutoQA code generation...")
    asyncio.run(main())
    print("Done")