import asyncio
import os
from agents import Agent, ModelSettings, Runner
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
    """Analiza el código existente en el repositorio objetivo"""
    analysis = {
        "page_objects": [],
        "test_classes": [],
        "utilities": [],
        "structure": {}
    }
    
    if not os.path.exists(base_path):
        return analysis
    
    # Buscar Page Objects existentes
    page_pattern = f"{base_path}/**/mapfre/paginas/*.java"
    for file_path in glob.glob(page_pattern, recursive=True):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            analysis["page_objects"].append({
                "file": file_path,
                "name": os.path.basename(file_path),
                "content": content[:500] + "..." if len(content) > 500 else content
            })
    
    # Buscar Tests existentes
    test_pattern = f"{base_path}/**/mapfre/casos/*.java"
    for file_path in glob.glob(test_pattern, recursive=True):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            analysis["test_classes"].append({
                "file": file_path,
                "name": os.path.basename(file_path),
                "content": content[:500] + "..." if len(content) > 500 else content
            })
    
    # Buscar utilidades existentes
    utils_pattern = f"{base_path}/**/mapfre/utils/*.java"
    for file_path in glob.glob(utils_pattern, recursive=True):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            analysis["utilities"].append({
                "file": file_path,
                "name": os.path.basename(file_path),
                "content": content[:500] + "..." if len(content) > 500 else content
            })
    
    return analysis

def analyze_framework_libraries():
    """Analiza las librerías del framework para entender funciones disponibles"""
    framework_analysis = {
        "libraries": []
    }
    
    # Obtener paths de librerías desde variables de entorno (separadas por comas)
    framework_lib_paths = os.environ.get("FRAMEWORK_LIB_PATHS", "../selenium-driver-lib,../selenium-commons-lib")
    lib_paths = [path.strip() for path in framework_lib_paths.split(",") if path.strip()]
    
    for lib_path in lib_paths:
        if os.path.exists(lib_path):
            lib_name = os.path.basename(lib_path)
            print(f"   📚 Analizando {lib_name} en: {lib_path}")
            
            lib_analysis = {
                "name": lib_name,
                "path": lib_path,
                "classes": []
            }
            
            java_pattern = f"{lib_path}/**/*.java"
            for file_path in glob.glob(java_pattern, recursive=True):
                if file_path.endswith('.java'):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            class_name = os.path.basename(file_path).replace('.java', '')
                            lib_analysis["classes"].append({
                                "name": class_name,
                                "file": file_path,
                                "content": content[:800] + "..." if len(content) > 800 else content
                            })
                    except Exception as e:
                        print(f"      ⚠️  Error leyendo {file_path}: {e}")
            
            framework_analysis["libraries"].append(lib_analysis)
            print(f"      📁 {len(lib_analysis['classes'])} clases encontradas")
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
    """Agrega contexto del código existente, librerías del framework y proyectos adicionales al prompt original"""
    context_addition = f"""

=== CONTEXTO AUTOMÁTICO AGREGADO POR AUTOQA ===

ANÁLISIS DEL PROYECTO OBJETIVO: {target_path}
============================================

CÓDIGO EXISTENTE ENCONTRADO:

Page Objects existentes ({len(code_analysis['page_objects'])} archivos):"""
    
    for po in code_analysis['page_objects']:
        context_addition += f"\n- {po['name']}:\n```java\n{po['content']}\n```\n"
    
    context_addition += f"\nClases de Test existentes ({len(code_analysis['test_classes'])} archivos):\n"
    for test in code_analysis['test_classes']:
        context_addition += f"\n- {test['name']}:\n```java\n{test['content']}\n```\n"
    
    context_addition += f"\nUtilidades existentes ({len(code_analysis['utilities'])} archivos):\n"
    for util in code_analysis['utilities']:
        context_addition += f"\n- {util['name']}:\n```java\n{util['content']}\n```\n"
    
    # Agregar análisis de las librerías del framework
    context_addition += f"\nLIBRERÍAS DEL FRAMEWORK DISPONIBLES:\n"
    for lib in framework_analysis['libraries']:
        context_addition += f"\n{lib['name'].upper()} ({len(lib['classes'])} clases):\n"
        for cls in lib['classes']:
            context_addition += f"\n- {cls['name']}:\n```java\n{cls['content']}\n```\n"
    
    # Agregar proyectos adicionales como contexto
    if additional_projects:
        context_addition += f"\nPROYECTOS DE REFERENCIA DESCARGADOS:\n"
        for project in additional_projects:
            context_addition += f"\n{project['name'].upper()} - {project['path']}:\n"
            context_addition += f"Estructura del proyecto:\n"
            for file_info in project['files'][:10]:  # Limitar a 10 archivos principales
                context_addition += f"- {file_info['name']}: {file_info['type']}\n"
                if file_info['type'] == 'java' and file_info.get('content'):
                    context_addition += f"```java\n{file_info['content'][:400]}...\n```\n"
    
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

# Crear agente
agent = Agent(
    model=MODEL,
    model_settings=ModelSettings(truncation="auto", reasoning={"summary": "auto"}),
    name="Code Generator and File Editor Agent",
    instructions=enhanced_prompt
)

# Función para extraer y crear archivos del código generado
# Funciones de extracción manual removidas - el agente crea archivos directamente

# Ejecutar agente
async def main():
    result = Runner.run_streamed(agent, enhanced_prompt, max_turns=MAX_TURNS)

    async for event in result.stream_events():
        if hasattr(event, "type") and event.type == "raw_response_event":
            data = event.data
            if hasattr(data, "type") and data.type == "response.reasoning_summary_text.done":
                print(f"🧠 Agent reasoning: {data.text}")

    print(f"📝 Generated code output:\n{result.final_output}")
    
    # Trabajar directamente en el repositorio objetivo
    if os.path.exists(TARGET_PROJECT_PATH):
        print(f"✅ Agente configurado para trabajar directamente en: {TARGET_PROJECT_PATH}")
        
        # Crear resumen de lo generado
        summary_file = f"{TARGET_PROJECT_PATH}/AutoQA-Generation-Summary.md"
        with open(summary_file, "w", encoding="utf-8") as f:
            f.write("# Resumen de Generación AutoQA\n\n")
            f.write(f"## Configuración\n\n")
            f.write(f"- **Modelo utilizado**: {MODEL}\n")
            f.write(f"- **Repositorio objetivo**: {TARGET_PROJECT_PATH}\n")
            f.write(f"- **Fecha de generación**: {os.environ.get('GITHUB_RUN_ID', 'Local')}\n\n")
            f.write(f"## Análisis Previo\n\n")
            f.write(f"### Código Existente en el Proyecto:\n")
            f.write(f"- Page Objects existentes: {len(code_analysis['page_objects'])}\n")
            f.write(f"- Tests existentes: {len(code_analysis['test_classes'])}\n")
            f.write(f"- Utilidades existentes: {len(code_analysis['utilities'])}\n\n")
            f.write(f"### Librerías del Framework Analizadas:\n")
            for lib in framework_analysis['libraries']:
                f.write(f"- Clases en {lib['name']}: {len(lib['classes'])}\n")
            f.write(f"\n### Proyectos Adicionales de Referencia:\n")
            for project in additional_projects:
                f.write(f"- {project['name']}: {len(project['files'])} archivos\n")
            f.write(f"\n## Output Completo del Agente\n\n")
            f.write(f"```\n{result.final_output}\n```\n")
        
        print(f"📋 Resumen guardado en: {summary_file}")
        print(f"📁 El agente debe haber creado los archivos Java directamente en el repositorio")
    else:
        print(f"❌ No se encontró el directorio objetivo: {TARGET_PROJECT_PATH}")
        print("   El agente no pudo trabajar directamente en el repositorio.")

if __name__ == "__main__":
    print("Starting AutoQA code generation...")
    asyncio.run(main())
    print("Done")
