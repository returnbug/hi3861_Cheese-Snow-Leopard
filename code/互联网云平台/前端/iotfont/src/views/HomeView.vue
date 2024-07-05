<template>
  <el-container class="layout-container-demo" style="height: 600px">
    <el-aside width="200px">
      <div class="logo">
        点云<img src="../image/PointCloud.svg" style="margin-left: 10px">
      </div>
      <el-menu :router="true" :default-active="'/table'">
        <el-menu-item index="/table" class="item">
          <el-icon>
            <View />
          </el-icon>
          <span class="item-text">点云管理</span>
        </el-menu-item>
        <el-menu-item index="/about" class="item">
          <el-icon>
            <ChatDotRound />
          </el-icon>
          <span class="item-text">联系我们</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header style="text-align: right; font-size: 12px; outline: none; background-color: white;">
        <div class="toolbar">
          <el-dropdown>
            <el-icon style="margin-right: 8px; margin-top: 1px; outline: none; cursor: pointer;">
              <setting />
            </el-icon>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item>View</el-dropdown-item>
                <el-dropdown-item>Add</el-dropdown-item>
                <el-dropdown-item>Delete</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
          <span>Tom</span>
        </div>
      </el-header>

      <el-main style="background: rgb(240,241,243);">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>


<script setup>


</script>

<style lang="scss" scoped>
.layout-container-demo .el-header {
  position: relative;
  background-color: var(--el-color-primary-light-7);
  color: var(--el-text-color-primary);
}

.layout-container-demo .el-aside {
  color: white;
  background: rgb(15, 16, 18)
}

.layout-container-demo .el-menu {
  border-right: none;
}

.layout-container-demo .el-main {
  padding: 0;
}

.layout-container-demo .toolbar {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  right: 20px;
}

.logo{
  display: flex;
  flex-direction: row;
  justify-content: center;
  align-items: center;
}

.item{
  background: rgb(15, 16, 18);
}


</style>