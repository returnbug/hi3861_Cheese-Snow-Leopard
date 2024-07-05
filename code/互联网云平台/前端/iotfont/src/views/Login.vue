<template>
    <Button type="primary" @click="btn">Primary</Button>
</template>
<script setup>
import {useRouter} from 'vue-router'
const router = useRouter()
const btn = () => {
    router.push('/home')
}
</script>