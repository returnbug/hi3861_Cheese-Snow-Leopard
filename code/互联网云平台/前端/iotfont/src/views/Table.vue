<template>
    <el-table :data="tableData" height="600px" style="width: 100%; margin-top: 10px; margin-left: 10px"
        :default-sort="{ prop: 'num', order: 'ascending' }">
        <el-table-column prop="num" label="序号" width="280" />
        <el-table-column prop="detec_time" label="检测时间" width="380" />
        <el-table-column label="Operation">
            <template #default="scope">
                <el-button size="mini" type="primary" @click="viewDetails(scope.row)">
                    查看
                </el-button>
                <el-button size="mini" type="danger" @click="handleDelete(scope.$index, scope.row)">
                    <el-icon>
                        <Delete />
                    </el-icon>
                </el-button>
            </template>
        </el-table-column>
    </el-table>
    <el-dialog v-model="centerDialogVisible" title="点云图片" width="500" align-center>
        <div class="images">
            <div class="block">
                <span class="demonstration">上</span>
                <el-image @click="goTop" style="width: 100px; height: 100px; margin-top: 5px" :src="url_top" :fit="fill"
                    class="img" />
            </div>
            <div class="block">
                <span class="demonstration">下</span>
                <el-image @click="goBottom" style="width: 100px; height: 100px; margin-top: 5px;" :src="url_bottom"
                    :fit="fill" class="img" />
            </div>
            <div class="block">
                <span class="demonstration">左</span>
                <el-image @click="goLeft" style="width: 100px; height: 100px; margin-top: 5px" :src="url_left"
                    :fit="fill" class="img" />
            </div>
            <div class="block">
                <span class="demonstration">右</span>
                <el-image @click="goRight" style="width: 100px; height: 100px; margin-top: 5px" :src="url_right"
                    :fit="fill" class="img" />
            </div>
        </div>
        <template #footer>
            <div class="dialog-footer">
                <el-button @click="centerDialogVisible = false">Cancel</el-button>
                <el-button type="primary" @click="centerDialogVisible = false">
                    Confirm
                </el-button>
            </div>
        </template>
    </el-dialog>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import API from '@/utils/API.js'
const centerDialogVisible = ref(false)
const url_top = ref('')
const url_bottom = ref('')
const url_left = ref('')
const url_right = ref('')
const tableData = ref([])
const route = useRouter()

API({
    url: '/getData',
    method: 'get',
}).then(res => {
    console.log(res.data)
    tableData.value = res.data
}).catch(err => {
    console.log(err)
})

const goTop = () => {
    route.push('/pcdLoader')
    sessionStorage.setItem('url', url_top.value)
}

const goBottom = () => {
    route.push('/pcdLoader')
    sessionStorage.setItem('url', url_bottom.value)
}

const goLeft = () => {
    route.push('/pcdLoader')
    sessionStorage.setItem('url', url_left.value)
}

const goRight = () => {
    route.push('/pcdLoader')
    sessionStorage.setItem('url', url_right.value)
}

const viewDetails = (row) => {
    centerDialogVisible.value = true
    API({
        url:'/getImage',
        method:'get',
        params:{
            num:row.num
        }
    }).then(res => {
        console.log(res.data.data)
        const data = res.data.data
        url_bottom.value = data[0]
        url_left.value = data[1]
        url_right.value = data[2]
        url_top.value = data[3]
    }).catch(err => {
        console.log(err)
    })
}

</script>

<style scoped>
.images {
    display: flex;
    justify-content: space-between;
    margin: 20px 0;
}
.block {
    display: flex;
    flex-direction: column;
    align-items: center;
}
.img{
    cursor: pointer;
}
</style>