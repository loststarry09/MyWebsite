<template>
  <div class="min-h-screen bg-[#F7F5F2] text-gray-800 transition-colors duration-300 dark:bg-gray-900 dark:text-gray-100">
    <header class="mx-auto max-w-5xl px-4 py-4 md:px-8 md:py-6 lg:px-16">
      <div class="flex items-center justify-between md:justify-start md:gap-4">
        <nav class="hidden md:flex md:items-center md:gap-4 md:text-base">
          <RouterLink to="/" class="transition-colors duration-200 hover:text-stone-600 hover:underline dark:hover:text-stone-300">首页</RouterLink>
          <RouterLink to="/blog" class="transition-colors duration-200 hover:text-stone-600 hover:underline dark:hover:text-stone-300">博客</RouterLink>
          <RouterLink to="/programs" class="transition-colors duration-200 hover:text-stone-600 hover:underline dark:hover:text-stone-300">我的程序</RouterLink>
          <RouterLink to="/fun" class="transition-colors duration-200 hover:text-stone-600 hover:underline dark:hover:text-stone-300">娱乐</RouterLink>
        </nav>
        <ThemeToggle
          :theme="currentTheme"
          :theme-storage-key="THEME_STORAGE_KEY"
          :apply-theme="applyTheme"
          @theme-change="handleThemeChange"
        />
        <button
          type="button"
          class="rounded p-2 text-gray-700 transition-colors hover:bg-stone-200 hover:text-stone-700 dark:text-gray-200 dark:hover:bg-gray-800 dark:hover:text-stone-200 md:hidden"
          aria-label="切换导航菜单"
          @click="isMenuOpen = !isMenuOpen"
        >
          <svg class="h-5 w-5" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
      </div>
      <nav
        v-if="isMenuOpen"
        class="mt-3 space-y-1 rounded-lg border border-stone-200 bg-white p-3 text-sm shadow-sm dark:border-gray-700 dark:bg-gray-800 md:hidden"
      >
        <RouterLink to="/" class="block rounded px-2 py-2 transition-colors duration-200 hover:bg-stone-100 dark:hover:bg-gray-700" @click="isMenuOpen = false">首页</RouterLink>
        <RouterLink to="/blog" class="block rounded px-2 py-2 transition-colors duration-200 hover:bg-stone-100 dark:hover:bg-gray-700" @click="isMenuOpen = false">博客</RouterLink>
        <RouterLink to="/programs" class="block rounded px-2 py-2 transition-colors duration-200 hover:bg-stone-100 dark:hover:bg-gray-700" @click="isMenuOpen = false">我的程序</RouterLink>
        <RouterLink to="/fun" class="block rounded px-2 py-2 transition-colors duration-200 hover:bg-stone-100 dark:hover:bg-gray-700" @click="isMenuOpen = false">娱乐</RouterLink>
      </nav>
    </header>
    <main class="mx-auto max-w-5xl px-4 pb-8 md:px-8 md:pb-10 lg:px-16">
      <RouterView v-slot="{ Component }">
        <Transition name="page-fade" mode="out-in">
          <component :is="Component" />
        </Transition>
      </RouterView>
    </main>
    <p class="fixed bottom-3 left-3 text-[11px] text-stone-400 transition-colors duration-300 dark:text-stone-500">
      版本：V1.2
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
const isMenuOpen = ref(false)
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
