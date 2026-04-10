<template>
  <div class="min-h-screen bg-[#F7F5F2] text-gray-800">
    <header class="mx-auto flex max-w-4xl gap-4 px-6 py-6 text-sm">
      <RouterLink to="/" class="hover:underline">首页</RouterLink>
      <RouterLink to="/programs" class="hover:underline">我的程序</RouterLink>
      <RouterLink to="/fun" class="hover:underline">娱乐</RouterLink>
    </header>
    <main class="mx-auto max-w-4xl px-6 pb-10">
      <RouterView />
    </main>
  </div>
</template>
