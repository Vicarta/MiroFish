<template>
  <div class="settings-page">
    <nav class="topbar">
      <router-link to="/" class="brand-link">MIROFISH</router-link>
      <router-link to="/" class="back-link">Back to home</router-link>
    </nav>

    <main class="settings-shell">
      <section class="hero-card">
        <div class="eyebrow">Runtime configuration</div>
        <h1 class="page-title">Settings</h1>
        <p class="page-copy">
          Configure the live deployment without exposing stored secret values in the browser. Secret fields below are always blank on load, and new credentials are validated before they are written.
        </p>
      </section>

      <section class="status-grid">
        <article class="status-card">
          <div class="status-label">LLM API key</div>
          <div class="status-value" :class="settings.llm_api_key_configured ? 'configured' : 'missing'">
            {{ settings.llm_api_key_configured ? 'Configured' : 'Missing' }}
          </div>
          <p class="status-copy">A saved key is required before graph generation, profile generation, and report creation can run.</p>
        </article>

        <article class="status-card">
          <div class="status-label">Zep API key</div>
          <div class="status-value" :class="settings.zep_api_key_configured ? 'configured' : 'missing'">
            {{ settings.zep_api_key_configured ? 'Configured' : 'Missing' }}
          </div>
          <p class="status-copy">This controls graph storage and memory retrieval. The current value is never returned to the UI.</p>
        </article>

        <article class="status-card">
          <div class="status-label">LLM base URL</div>
          <div class="status-inline-value">{{ settings.llm_base_url || 'Not set' }}</div>
        </article>

        <article class="status-card">
          <div class="status-label">LLM model</div>
          <div class="status-inline-value">{{ settings.llm_model_name || 'Not set' }}</div>
        </article>
      </section>

      <section class="form-card">
        <div class="form-header">
          <div>
            <div class="form-eyebrow">Write-only update</div>
            <h2 class="form-title">Rotate or add credentials</h2>
          </div>
          <div v-if="loading" class="form-badge">Validating…</div>
        </div>

        <div v-if="successMessage" class="notice success">{{ successMessage }}</div>
        <div v-if="errorMessage" class="notice error">{{ errorMessage }}</div>

        <form class="settings-form" @submit.prevent="handleSubmit">
          <label class="field">
            <span class="field-label">LLM API key</span>
            <input
              v-model="form.llm_api_key"
              ref="llmApiKeyInput"
              class="field-input"
              type="password"
              name="runtime-llm-api-key"
              autocomplete="off"
              autocapitalize="off"
              autocorrect="off"
              spellcheck="false"
              data-1p-ignore="true"
              data-lpignore="true"
              placeholder="Enter a new LLM API key to add or replace the stored value"
              @focus="clearSecretField('llm_api_key')"
            />
            <span class="field-hint">Leave blank to keep the currently stored key.</span>
          </label>

          <label class="field">
            <span class="field-label">Zep API key</span>
            <input
              v-model="form.zep_api_key"
              ref="zepApiKeyInput"
              class="field-input"
              type="password"
              name="runtime-zep-api-key"
              autocomplete="off"
              autocapitalize="off"
              autocorrect="off"
              spellcheck="false"
              data-1p-ignore="true"
              data-lpignore="true"
              placeholder="Enter a new Zep API key to add or replace the stored value"
              @focus="clearSecretField('zep_api_key')"
            />
            <span class="field-hint">Leave blank to keep the currently stored key.</span>
          </label>

          <label class="field">
            <span class="field-label">LLM base URL</span>
            <input
              v-model="form.llm_base_url"
              class="field-input"
              type="url"
              placeholder="https://api.openai.com/v1"
            />
            <span class="field-hint">This value is not treated as a secret and is shown in the status panel.</span>
          </label>

          <label class="field">
            <span class="field-label">LLM model name</span>
            <input
              v-model="form.llm_model_name"
              class="field-input"
              type="text"
              placeholder="gpt-4o-mini"
            />
            <span class="field-hint">Use this to point the deployment at a different OpenAI-compatible model.</span>
          </label>

          <div class="actions">
            <button class="primary-action" type="submit" :disabled="loading">
              {{ loading ? 'Validate and save…' : 'Validate and save settings' }}
            </button>
          </div>
        </form>
      </section>
    </main>
  </div>
</template>

<script setup>
import { nextTick, onMounted, reactive, ref } from 'vue'
import { getSettings, updateSettings } from '../api/settings'

const loading = ref(false)
const successMessage = ref('')
const errorMessage = ref('')
const llmApiKeyInput = ref(null)
const zepApiKeyInput = ref(null)

const settings = reactive({
  llm_api_key_configured: false,
  zep_api_key_configured: false,
  llm_base_url: '',
  llm_model_name: ''
})

const form = reactive({
  llm_api_key: '',
  zep_api_key: '',
  llm_base_url: '',
  llm_model_name: ''
})

const syncFormFromSettings = () => {
  form.llm_api_key = ''
  form.zep_api_key = ''
  form.llm_base_url = settings.llm_base_url || ''
  form.llm_model_name = settings.llm_model_name || ''
}

const clearSecretField = (fieldName) => {
  form[fieldName] = ''
}

const clearSecretInputs = async () => {
  await nextTick()

  if (llmApiKeyInput.value) {
    llmApiKeyInput.value.value = ''
  }
  if (zepApiKeyInput.value) {
    zepApiKeyInput.value.value = ''
  }

  form.llm_api_key = ''
  form.zep_api_key = ''
}

const applySettings = (payload) => {
  settings.llm_api_key_configured = Boolean(payload.llm_api_key_configured)
  settings.zep_api_key_configured = Boolean(payload.zep_api_key_configured)
  settings.llm_base_url = payload.llm_base_url || ''
  settings.llm_model_name = payload.llm_model_name || ''
  syncFormFromSettings()
}

const loadSettings = async () => {
  errorMessage.value = ''

  try {
    const response = await getSettings()
    applySettings(response.data)
    await clearSecretInputs()
  } catch (error) {
    errorMessage.value = error.response?.data?.error || error.message || 'Failed to load settings.'
  }
}

const handleSubmit = async () => {
  loading.value = true
  successMessage.value = ''
  errorMessage.value = ''

  try {
    const response = await updateSettings({
      llm_api_key: form.llm_api_key,
      zep_api_key: form.zep_api_key,
      llm_base_url: form.llm_base_url,
      llm_model_name: form.llm_model_name
    })

    applySettings(response.data.status)
    successMessage.value = 'Settings validated and saved. Stored secret values remain hidden and blank in the UI.'
    await clearSecretInputs()
  } catch (error) {
    errorMessage.value = error.response?.data?.error || error.message || 'Failed to validate settings.'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadSettings()
  setTimeout(() => {
    clearSecretInputs()
  }, 300)
})
</script>

<style scoped>
.settings-page {
  min-height: 100vh;
  background:
    radial-gradient(circle at top left, rgba(255, 127, 80, 0.12), transparent 28%),
    radial-gradient(circle at bottom right, rgba(0, 0, 0, 0.08), transparent 30%),
    #f6f3ee;
  color: #111;
}

.topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 28px 36px 0;
}

.brand-link,
.back-link {
  text-decoration: none;
  color: #111;
}

.brand-link {
  font-family: 'JetBrains Mono', monospace;
  font-weight: 800;
  letter-spacing: 0.08em;
}

.back-link {
  border: 1px solid #111;
  padding: 10px 14px;
  font-size: 0.85rem;
  transition: background 0.2s ease, color 0.2s ease;
}

.back-link:hover {
  background: #111;
  color: #fff;
}

.settings-shell {
  max-width: 1120px;
  margin: 0 auto;
  padding: 32px 36px 64px;
}

.hero-card,
.form-card,
.status-card {
  border: 1px solid rgba(17, 17, 17, 0.12);
  background: rgba(255, 255, 255, 0.88);
  backdrop-filter: blur(12px);
}

.hero-card {
  padding: 28px;
}

.eyebrow,
.form-eyebrow {
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: #f05a28;
  font-weight: 700;
}

.page-title {
  margin-top: 10px;
  font-size: clamp(2rem, 4vw, 3.5rem);
  line-height: 0.95;
}

.page-copy {
  max-width: 760px;
  margin-top: 16px;
  font-size: 1rem;
  line-height: 1.6;
  color: rgba(17, 17, 17, 0.7);
}

.status-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18px;
  margin-top: 18px;
}

.status-card {
  padding: 22px;
}

.status-label {
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: rgba(17, 17, 17, 0.58);
}

.status-value {
  margin-top: 16px;
  display: inline-flex;
  align-items: center;
  padding: 8px 12px;
  font-size: 0.82rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.status-value.configured {
  background: #111;
  color: #fff;
}

.status-value.missing {
  background: #ffe2d7;
  color: #9c2c05;
}

.status-inline-value {
  margin-top: 16px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.95rem;
  line-height: 1.5;
  word-break: break-all;
}

.status-copy {
  margin-top: 14px;
  color: rgba(17, 17, 17, 0.7);
  line-height: 1.6;
}

.form-card {
  margin-top: 18px;
  padding: 28px;
}

.form-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
}

.form-title {
  margin-top: 8px;
  font-size: 1.8rem;
}

.form-badge {
  border: 1px solid #111;
  padding: 8px 12px;
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.notice {
  margin-top: 18px;
  padding: 14px 16px;
  font-size: 0.95rem;
  line-height: 1.5;
}

.notice.success {
  background: #edf8ef;
  color: #20552c;
}

.notice.error {
  background: #fff0ed;
  color: #8b1e00;
}

.settings-form {
  margin-top: 24px;
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18px;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.field-label {
  font-size: 0.82rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  font-weight: 700;
}

.field-input {
  width: 100%;
  border: 1px solid rgba(17, 17, 17, 0.18);
  background: #fff;
  color: #111;
  padding: 14px 16px;
  font-size: 0.96rem;
}

.field-input:focus {
  outline: none;
  border-color: #111;
}

.field-hint {
  color: rgba(17, 17, 17, 0.62);
  font-size: 0.88rem;
  line-height: 1.5;
}

.actions {
  grid-column: 1 / -1;
  display: flex;
  justify-content: flex-start;
  margin-top: 8px;
}

.primary-action {
  border: none;
  background: #111;
  color: #fff;
  padding: 14px 22px;
  font-size: 0.92rem;
  font-weight: 700;
  cursor: pointer;
}

.primary-action:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

@media (max-width: 900px) {
  .status-grid,
  .settings-form {
    grid-template-columns: 1fr;
  }

  .topbar,
  .settings-shell {
    padding-left: 20px;
    padding-right: 20px;
  }

  .topbar {
    padding-top: 20px;
  }
}

@media (max-width: 640px) {
  .topbar {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .hero-card,
  .form-card,
  .status-card {
    padding: 20px;
  }
}
</style>
