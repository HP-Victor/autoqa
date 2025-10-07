# AutoQA - Computer Use Agent

## 🚨 IMPORTANTE: OpenAI ya no soporta Computer Use

**OpenAI ha descontinuado completamente `computer_use_preview`** en todos sus modelos (incluyendo GPT-5). 

## ✅ Solución: Usar Anthropic Claude

**Claude sí tiene computer use funcionando correctamente.**

### 🔧 Configuración recomendada:

1. **Obtener API key de Anthropic:**
   - Ve a: https://console.anthropic.com/
   - Crea una cuenta y obtén tu API key
   - Claude-3.5-Sonnet tiene excelentes capacidades de computer use

2. **Configurar en GitHub Secrets:**
   ```
   ANTHROPIC_API_KEY=tu-api-key-de-anthropic
   ```

3. **Ejecutar el workflow:**
   - El sistema detectará automáticamente Anthropic y usará Claude
   - Si solo tienes OpenAI, mostrará advertencias pero intentará funcionar

### 📋 Modelos disponibles:

| Proveedor | Modelo | Computer Use | Estado |
|-----------|--------|-------------|---------|
| **Anthropic** | claude-3-5-sonnet-20241022 | ✅ **SÍ** | **Recomendado** |
| OpenAI | gpt-5-pro | ❌ No | Descontinuado |
| OpenAI | gpt-4o | ❌ No | Descontinuado |
| OpenAI | gpt-4o-mini | ❌ No | Nunca lo tuvo |

### 🎯 Uso del workflow:

```yaml
# En tu workflow de GitHub Actions:
uses: HP-Victor/autoqa/.github/workflows/reusable-autoqa.yml@main
secrets:
  ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}  # ✅ Recomendado
  # OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}      # ⚠️ No funciona para computer use
with:
  prompt: "Tu tarea de automatización aquí"
```

### 🔄 Migración desde OpenAI:

Si venías usando OpenAI:

1. **Obtén una API key de Anthropic** (ver arriba)
2. **Añádela a tus GitHub Secrets** como `ANTHROPIC_API_KEY`
3. **Ejecuta el workflow** - automáticamente usará Claude
4. **Opcionalmente** puedes remover `OPENAI_API_KEY` (pero no es necesario)

### 💰 Costos aproximados:

- **Claude-3.5-Sonnet:** ~$3-15/1M tokens (computer use incluido)
- **OpenAI GPT-4o:** ~$15-30/1M tokens (computer use NO disponible)

### 🐛 Solución de problemas:

**Error:** `computer_use_preview is not supported`
- ✅ **Solución:** Configura `ANTHROPIC_API_KEY`

**Error:** `No API key found`
- ✅ **Solución:** Añade `ANTHROPIC_API_KEY` a tus secrets

**Funciona pero no hace computer use:**
- ✅ **Verificar:** Que tengas `ANTHROPIC_API_KEY` configurado
- ✅ **Verificar:** Que el workflow use el secret correcto

### 📚 Documentación adicional:

- [Anthropic Console](https://console.anthropic.com/)
- [Claude Computer Use Guide](https://docs.anthropic.com/)
- [GitHub Secrets Setup](https://docs.github.com/en/actions/security-guides/encrypted-secrets)

---

## 🕰️ Historial del problema:

- **2024 temprano:** OpenAI `computer_use_preview` funcionaba
- **2024 medio:** Empezaron las restricciones  
- **2024 tardío:** Solo gpt-4o específicos
- **2025:** **Completamente descontinuado** en OpenAI
- **Ahora:** Solo Anthropic Claude soporta computer use

**TL;DR: Usa Anthropic Claude, no OpenAI, para computer use.** 🎯