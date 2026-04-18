<template>
  <div class="min-h-screen bg-[#F7F5F2] text-gray-800 transition-colors duration-300 dark:bg-gray-900 dark:text-gray-100">
    <header class="mx-auto flex max-w-4xl gap-4 px-6 py-6 text-base">
      <RouterLink to="/" class="transition-colors duration-200 hover:text-stone-600 hover:underline dark:hover:text-stone-300">首页</RouterLink>
      <RouterLink to="/blog" class="transition-colors duration-200 hover:text-stone-600 hover:underline dark:hover:text-stone-300">博客</RouterLink>
      <RouterLink to="/programs" class="transition-colors duration-200 hover:text-stone-600 hover:underline dark:hover:text-stone-300">我的程序</RouterLink>
      <RouterLink to="/fun" class="transition-colors duration-200 hover:text-stone-600 hover:underline dark:hover:text-stone-300">娱乐</RouterLink>
      <ThemeToggle
        :theme="currentTheme"
        :theme-storage-key="THEME_STORAGE_KEY"
        :apply-theme="applyTheme"
        @theme-change="handleThemeChange"
      />
    </header>
    <main class="mx-auto max-w-4xl px-6 pb-10">
      <RouterView v-slot="{ Component }">
        <Transition name="page-fade" mode="out-in">
          <component :is="Component" />
        </Transition>
      </RouterView>
    </main>
    <p class="fixed bottom-3 left-3 text-[11px] text-stone-400 transition-colors duration-300 dark:text-stone-500">
      版本：MyWebsite
    </p>
  </div>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'
import ThemeToggle from './components/ThemeToggle.vue'

const THEME_STORAGE_KEY = 'theme'
const DEFAULT_THEME = 'system'
const SYSTEM_THEME_QUERY = '(prefers-color-scheme: dark)'

const currentTheme = ref(DEFAULT_THEME)
let systemThemeMediaQuery

const getStoredTheme = () => {
  const storedTheme = localStorage.getItem(THEME_STORAGE_KEY)

  if (storedTheme === 'light' || storedTheme === 'dark' || storedTheme === 'system') {
    return storedTheme
  }

  return DEFAULT_THEME
}

const applyTheme = (theme) => {
  const root = document.documentElement
  const isSystemDark = window.matchMedia(SYSTEM_THEME_QUERY).matches

  if (theme === 'dark') {
    root.classList.add('dark')
    return
  }

  if (theme === 'light') {
    root.classList.remove('dark')
    return
  }

  if (isSystemDark) {
    root.classList.add('dark')
  } else {
    root.classList.remove('dark')
  }
}

const handleSystemThemeChange = () => {
  if (currentTheme.value === 'system') {
    applyTheme('system')
  }
}

const handleThemeChange = (theme) => {
  currentTheme.value = theme
}

onMounted(() => {
  currentTheme.value = getStoredTheme()
  applyTheme(currentTheme.value)

  systemThemeMediaQuery = window.matchMedia(SYSTEM_THEME_QUERY)
  systemThemeMediaQuery.addEventListener('change', handleSystemThemeChange)
})

onBeforeUnmount(() => {
  systemThemeMediaQuery?.removeEventListener('change', handleSystemThemeChange)
})
</script>

<style scoped>
.page-fade-enter-active,
.page-fade-leave-active {
  transition: opacity 220ms ease, transform 220ms ease;
}

.page-fade-enter-from,
.page-fade-leave-to {
  opacity: 0;
  transform: translateY(6px);
}
</style>
