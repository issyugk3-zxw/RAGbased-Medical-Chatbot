<template>
  <div class="self-container">
    <!-- 左侧：个人基本信息 -->
    <div class="profile-container glass-card">
      <div class="profile-header">
        <h2 class="user-name">{{ userInfo.name || '用户' }}</h2>
        <div class="user-id">ID: {{ userInfo.id || 'N/A' }}</div>
      </div>
      
      <el-divider content-position="center">基本信息</el-divider>
      
      <div class="profile-info">
        <div class="info-item">
          <div class="info-label">年龄</div>
          <div class="info-value" v-if="!isEditing">{{ userInfo.age ?? '未填写' }}岁</div>
          <el-input v-else v-model.number="userInfo.age" size="small" placeholder="请输入年龄">
            <template #append>岁</template>
          </el-input>
        </div>
        <div class="info-item">
          <div class="info-label">性别</div>
          <div class="info-value" v-if="!isEditing">{{ userInfo.gender === 'male' ? '男' : (userInfo.gender === 'female' ? '女' : '未填写') }}</div>
          <el-select v-else v-model="userInfo.gender" size="small" placeholder="请选择性别" style="width: 100%;">
            <el-option label="男" value="male"></el-option>
            <el-option label="女" value="female"></el-option>
            <el-option label="未选择" value=""></el-option>
          </el-select>
        </div>
        <div class="info-item">
          <div class="info-label">血型</div>
          <div class="info-value" v-if="!isEditing">{{ userInfo.bloodType || '未填写' }}</div>
          <el-input v-else v-model="userInfo.bloodType" size="small" placeholder="请输入血型"></el-input>
        </div>
        <div class="info-item">
          <div class="info-label">身高</div>
          <div class="info-value" v-if="!isEditing">{{ userInfo.height ?? '未填写' }}cm</div>
          <el-input v-else v-model.number="userInfo.height" size="small" placeholder="请输入身高">
            <template #append>cm</template>
          </el-input>
        </div>
        <div class="info-item">
          <div class="info-label">体重</div>
          <div class="info-value" v-if="!isEditing">{{ userInfo.weight ?? '未填写' }}kg</div>
          <el-input v-else v-model.number="userInfo.weight" size="small" placeholder="请输入体重">
            <template #append>kg</template>
          </el-input>
        </div>
      </div>
      
      <el-divider content-position="center">联系方式</el-divider>
      
      <div class="profile-info">
        <div class="info-item">
          <div class="info-label">手机</div>
          <div class="info-value" v-if="!isEditing">{{ userInfo.phone || '未填写' }}</div>
          <el-input v-else v-model="userInfo.phone" size="small" placeholder="请输入手机号"></el-input>
        </div>
        <div class="info-item">
          <div class="info-label">邮箱</div>
          <div class="info-value" v-if="!isEditing">{{ userInfo.email || '未填写' }}</div>
          <el-input v-else v-model="userInfo.email" size="small" placeholder="请输入邮箱"></el-input>
        </div>
        <div class="info-item">
          <div class="info-label">紧急联系人</div>
          <div class="info-value" v-if="!isEditing">{{ userInfo.emergencyContact || '未填写' }}</div>
          <el-input v-else v-model="userInfo.emergencyContact" size="small" placeholder="请输入紧急联系人"></el-input>
        </div>
      </div>
      
      <div class="edit-profile">
        <el-button :type="isEditing ? 'danger' : 'primary'" size="small" @click="toggleEditMode" :disabled="!userid">
          <el-icon><EditPen /></el-icon>
          {{ isEditing ? '保存资料' : '编辑资料' }}
        </el-button>
      </div>
    </div>
    
    <!-- 右侧：健康记录和记忆 -->
    <div class="right-panel">
      <!-- 上半部分：健康记录时间线 -->
      <div class="health-timeline glass-card">
        <div class="section-header">
          <h3>健康记录</h3>
          <div class="edit-actions">
            <!-- 编辑模式下显示添加按钮 -->
            <el-button v-if="isHealthRecordEditing" type="success" size="small" @click="addHealthRecord">
              <el-icon><Plus /></el-icon>
              添加记录
            </el-button>
            
            <!-- 编辑/保存按钮 -->
            <el-button 
              :type="isHealthRecordEditing ? 'danger' : 'primary'" 
              size="small" 
              @click="toggleHealthRecordEditMode"
            >
              <el-icon v-if="!isHealthRecordEditing"><EditPen /></el-icon>
              <el-icon v-else><ElIcon><OfficeBuilding /></ElIcon></el-icon>
              {{ isHealthRecordEditing ? '保存记录' : '编辑记录' }}
            </el-button>
          </div>
        </div>
        
        <el-scrollbar height="320px">
          <div v-if="healthRecords.length === 0" class="no-records-message">
            暂无健康记录，请点击"{{ isHealthRecordEditing ? '添加记录' : '编辑记录' }}"{{ isHealthRecordEditing ? '' : '进入编辑模式' }}。
          </div>
          <el-timeline v-else>
            <el-timeline-item
              v-for="record in healthRecords"
              :key="record.id"
              :timestamp="formatDate(record.date)"
              :hollow="true"
              size="large"
            >
              <div class="timeline-card">
                <p class="record-description">{{ record.description }}</p>
                <div class="record-tags">
                  <el-tag 
                    v-for="tag in record.tags" 
                    :key="tag" 
                    size="small" 
                    :type="tagColorMap[getTagType(tag)]"
                    effect="light"
                  >
                    {{ tagTypeMap[getTagType(tag)] || tag }}
                  </el-tag>
                </div>
                <div class="record-actions">
                  <!-- 编辑模式下显示编辑和删除按钮 -->
                  <el-button v-if="isHealthRecordEditing" type="text" size="small" @click="editHealthRecord(record.id)">
                    <el-icon><EditPen /></el-icon>
                  </el-button>
                  <el-button v-if="isHealthRecordEditing" type="text" size="small" @click="deleteHealthRecord(record.id)">
                    <el-icon><Delete /></el-icon>
                  </el-button>
                </div>
              </div>
            </el-timeline-item>
          </el-timeline>
        </el-scrollbar>
      </div>
      
      <!-- 下半部分：记忆管理 -->
      <div class="memory-container glass-card">
        <div class="section-header">
          <h3>个人记忆</h3>
          <el-button type="primary" size="small" @click="addMemory">
            <el-icon><Plus /></el-icon>
            添加记忆
          </el-button>
        </div>
        
        <el-scrollbar height="250px">
          <div class="memory-list">
            <div v-for="memory in memories" :key="memory.id" class="memory-card">
              <div class="memory-content">{{ memory.content }}</div>
              <div class="memory-actions">
                <el-tooltip content="编辑" placement="top">
                  <el-button circle size="small" @click="editMemory(memory.id)">
                    <el-icon><EditPen /></el-icon>
                  </el-button>
                </el-tooltip>
                <el-tooltip content="删除" placement="top">
                  <el-button circle size="small" type="danger" @click="deleteMemory(memory.id)">
                    <el-icon><Delete /></el-icon>
                  </el-button>
                </el-tooltip>
              </div>
            </div>
          </div>
        </el-scrollbar>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, inject, reactive } from 'vue'
import {
  ElButton, ElDivider, ElTag, ElTimeline, ElTimelineItem, 
  ElScrollbar, ElTooltip, ElIcon, ElMessage, ElInput, ElSelect, ElOption, ElDatePicker, ElMessageBox
} from 'element-plus'
import {
  Edit, EditPen, Delete, Plus, Warning, Clock,
  OfficeBuilding, Sunny
} from '@element-plus/icons-vue'
import axios from 'axios'
import { useUserStore } from '../pinia/user'

interface UserSelfData {
  id?: string;
  name?: string;
  age?: number | null;
  gender?: 'male' | 'female' | '';
  bloodType?: string;
  height?: number | null;
  weight?: number | null;
  phone?: string;
  email?: string;
  emergencyContact?: string;
}

interface HealthRecord {
  id: string; // Client-side unique ID for list management
  description: string;
  date: number; // timestamp
  tags: string[];
  // title and type removed
}

// 添加Memory类型定义
interface Memory {
  id: string;
  content: string;
}

const userStore = inject<ReturnType<typeof useUserStore> | undefined>('userStore')
const userInfo = ref<Partial<UserSelfData>>({}) 
const userid = localStorage.getItem('userid')
const isEditing = ref(false)

// 健康记录
const healthRecords = ref<HealthRecord[]>([])
const isHealthRecordEditing = ref(false)

// 记忆数据
const memories = ref<Memory[]>([])


const formatDate = (timestamp: number): string => {
  const date = new Date(timestamp)
  return date.toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' })
}

type TimelineItemType = 'primary' | 'success' | 'warning' | 'danger' | 'info';

const getRecordType = (type: string): TimelineItemType => {
  switch (type) {
    case 'illness': return 'warning'
    case 'checkup': return 'success'
    case 'treatment': return 'primary'
    case 'vaccination': return 'info'
    default: return 'info'
  }
}

const getRecordColor = (type: string): string => {
  switch (type) {
    case 'illness': return '#E6A23C'
    case 'checkup': return '#67C23A'
    case 'treatment': return '#409EFF'
    case 'vaccination': return '#909399'
    default: return '#909399'
  }
}

// 添加标签类型映射
const tagTypeMap: { [key: string]: string } = {
  'illness': '疾病',
  'checkup': '检查',
  'treatment': '治疗',
  'vaccination': '疫苗接种'
}

// 添加标签颜色映射
const tagColorMap: { [key: string]: 'success' | 'warning' | 'info' | 'primary' | 'danger' } = {
  'illness': 'warning',
  'checkup': 'success',
  'treatment': 'primary',
  'vaccination': 'info'
}

// 获取标签类型
const getTagType = (tag: string): string => {
  // 将标签转换为小写以进行匹配
  const lowerTag = tag.toLowerCase()
  // 检查是否包含关键词
  if (lowerTag.includes('病') || lowerTag.includes('症') || lowerTag.includes('痛')) return 'illness'
  if (lowerTag.includes('检查') || lowerTag.includes('体检') || lowerTag.includes('化验')) return 'checkup'
  if (lowerTag.includes('治疗') || lowerTag.includes('用药') || lowerTag.includes('手术')) return 'treatment'
  if (lowerTag.includes('疫苗') || lowerTag.includes('接种')) return 'vaccination'
  return 'info' // 默认类型
}

const toggleEditMode = async () => {
  if (!userid) {
    ElMessage.error('用户未登录。');
    return;
  }

  if (isEditing.value) { // Current is save state
    try {
      const dataToSave = JSON.parse(JSON.stringify(userInfo.value));
      await axios.post('/userapi/updateSelfInfo/', {
        userid: userid,
        update_data: dataToSave
      });
      ElMessage.success('资料保存成功！');
      isEditing.value = false;
    } catch (error) {
      console.error('保存资料失败:', error);
      ElMessage.error('资料保存失败，请稍后再试。');
    }
  } else { // Current is view state, switch to edit
    try {
      const response = await axios.get('/userapi/getSelfInfo/', {
        params: { userid: userid }
      });
      if (response.data.status === 'success') {
        userInfo.value = response.data.info || { id: userid };
      } else {
        userInfo.value = { id: userid };
      }
      isEditing.value = true;
    } catch (error) {
      console.error('获取用户信息失败:', error);
      ElMessage.error('获取用户信息失败，请稍后再试。');
      userInfo.value = { id: userid };
      isEditing.value = true;
    }
  }
};

// 进入编辑健康记录模式
const toggleHealthRecordEditMode = async () => {
  if (!userStore) {
    ElMessage.error('用户数据存储功能不可用。');
    return;
  }
  
  if (isHealthRecordEditing.value) { // 当前是保存状态
    // 保存所有记录
    const saved = await saveHealthRecords();
    if (saved) {
      isHealthRecordEditing.value = false;
    }
  } else { // 当前是查看状态，切换到编辑
    isHealthRecordEditing.value = true;
  }
};

// 保存健康记录到后端
const saveHealthRecords = async () => {
  if (!userid) {
    ElMessage.error('用户未登录。');
    return false;
  }
  try {
    await axios.post('/userapi/updateHealthInfo/', {
      userid: userid,
      update_data: healthRecords.value
    });
    ElMessage.success('健康记录已成功更新！');
    return true;
  } catch (error) {
    console.error('保存健康记录失败:', error);
    ElMessage.error('健康记录保存失败，请稍后再试。');
    return false;
  }
};

// 添加健康记录
const addHealthRecord = async () => {
  if (!userStore) {
    ElMessage.error('用户数据存储功能不可用。');
    return;
  }
  
  try {
    const { value: description } = await ElMessageBox.prompt('请输入健康记录描述', '添加健康记录', {
      confirmButtonText: '确认',
      cancelButtonText: '取消',
      inputPlaceholder: '请输入描述内容'
    });
    
    if (!description || !description.trim()) {
      ElMessage.warning('记录描述不能为空。');
      return;
    }
    
    // 获取标签
    const { value: tagsInput } = await ElMessageBox.prompt('请输入标签(用逗号或空格分隔)', '添加健康记录', {
      confirmButtonText: '确认',
      cancelButtonText: '取消',
      inputPlaceholder: '可选：疾病,检查，治疗，疫苗接种'
    });
    
    const tags = tagsInput ? tagsInput.split(/[,\s]+/).map(tag => tag.trim()).filter(tag => tag) : [];
    
    // 获取日期
    const { value: dateInput } = await ElMessageBox.prompt('请输入日期(YYYY-MM-DD格式)', '添加健康记录', {
      confirmButtonText: '确认',
      cancelButtonText: '取消',
      inputValue: new Date().toISOString().split('T')[0],
      inputPlaceholder: 'YYYY-MM-DD'
    });
    
    let timestamp = Date.now();
    try {
      if (dateInput) {
        timestamp = new Date(dateInput).getTime();
        if (isNaN(timestamp)) {
          ElMessage.warning('日期格式无效，将使用当前时间。');
          timestamp = Date.now();
        }
      }
    } catch (e) {
      ElMessage.warning('日期格式无效，将使用当前时间。');
      timestamp = Date.now();
    }
    
    const newRecord: HealthRecord = {
      id: `client_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`, // 生成客户端ID
      description: description.trim(),
      date: timestamp,
      tags: tags
    };
    
    healthRecords.value.unshift(newRecord); // 添加到顶部
    
    if (!isHealthRecordEditing.value) {
      // 如果不是编辑模式，立即保存
      const saved = await saveHealthRecords();
      if (!saved) {
        // 如果保存失败，撤销更改
        healthRecords.value.shift();
        ElMessage.error('添加记录失败，更改已撤销。');
      }
    } else {
      // 在编辑模式下，记录会在用户点击保存按钮时一并保存
      // 按日期重新排序，保证最新的记录在最前面
      healthRecords.value.sort((a, b) => b.date - a.date);
    }
  } catch (e) {
    // 用户取消操作
    if (e !== 'cancel') {
      console.error('添加记录时发生错误:', e);
      ElMessage.error('添加记录失败: ' + e);
    }
  }
};

// 编辑单个健康记录
const editHealthRecord = async (id: string) => {
  if (!isHealthRecordEditing.value) {
    ElMessage.warning('请先点击"编辑记录"按钮进入编辑模式。');
    return;
  }
  
  const recordIndex = healthRecords.value.findIndex(r => r.id === id);
  if (recordIndex === -1) {
    ElMessage.error('未找到要编辑的记录。');
    return;
  }
  
  const record = healthRecords.value[recordIndex];
  
  try {
    // 获取新的描述
    const { value: newDescription } = await ElMessageBox.prompt('编辑记录描述', '编辑健康记录', {
      confirmButtonText: '确认',
      cancelButtonText: '取消',
      inputValue: record.description,
      inputPlaceholder: '请输入描述内容'
    });
    
    if (!newDescription || !newDescription.trim()) {
      ElMessage.warning('记录描述不能为空。');
      return;
    }
    
    // 获取新的标签
    const { value: newTagsInput } = await ElMessageBox.prompt('编辑标签(用逗号或空格分隔)', '编辑健康记录', {
      confirmButtonText: '确认',
      cancelButtonText: '取消',
      inputValue: record.tags.join(', '),
      inputPlaceholder: '例如: 发热,头痛 感冒'
    });
    
    const newTags = newTagsInput ? newTagsInput.split(/[,\s]+/).map(tag => tag.trim()).filter(tag => tag) : [];
    
    // 获取新的日期
    const { value: dateInput } = await ElMessageBox.prompt('编辑日期(YYYY-MM-DD格式)', '编辑健康记录', {
      confirmButtonText: '确认',
      cancelButtonText: '取消',
      inputValue: new Date(record.date).toISOString().split('T')[0],
      inputPlaceholder: 'YYYY-MM-DD'
    });
    
    let timestamp = record.date;
    try {
      if (dateInput) {
        const newTimestamp = new Date(dateInput).getTime();
        if (!isNaN(newTimestamp)) {
          timestamp = newTimestamp;
        } else {
          ElMessage.warning('日期格式无效，将保留原日期。');
        }
      }
    } catch (e) {
      ElMessage.warning('日期格式无效，将保留原日期。');
    }
    
    // 应用更改
    healthRecords.value[recordIndex] = {
      ...record,
      description: newDescription.trim(),
      tags: newTags,
      date: timestamp
    };
    
    // 重新排序，保证最新的记录在最前面
    healthRecords.value.sort((a, b) => b.date - a.date);
    
    ElMessage.success('记录已更新，请记得点击保存按钮以保存所有更改。');
  } catch (e) {
    // 用户取消操作
    if (e !== 'cancel') {
      console.error('编辑记录时发生错误:', e);
      ElMessage.error('编辑记录失败: ' + e);
    }
  }
};

// 删除健康记录
const deleteHealthRecord = async (id: string) => {
  if (!userStore) {
    ElMessage.error('用户数据存储功能不可用。');
    return;
  }
  
  try {
    // 使用Element Plus确认框代替原生confirm
    await ElMessageBox.confirm('确定要删除这条记录吗？此操作不可逆。', '删除确认', {
      confirmButtonText: '确认删除',
      cancelButtonText: '取消',
      type: 'warning'
    });
    
    const initialLength = healthRecords.value.length;
    healthRecords.value = healthRecords.value.filter(record => record.id !== id);
    
    if (healthRecords.value.length < initialLength) {
      if (!isHealthRecordEditing.value) {
        // 如果不在编辑模式，立即保存更改
        ElMessage.info('记录已在本地删除，正在同步到服务器...');
        await saveHealthRecords();
      } else {
        ElMessage.success('记录已删除，请记得点击保存按钮以保存所有更改。');
      }
    } else {
      ElMessage.warning('未找到要删除的记录，或记录之前已被删除。');
    }
  } catch (e) {
    // 用户取消删除操作
    if (e !== 'cancel') {
      console.error('删除记录时发生错误:', e);
      ElMessage.error('删除记录失败: ' + e);
    }
  }
};

// 添加记忆
const addMemory = async () => {
  if (!userid) {
    ElMessage.error('用户未登录。');
    return;
  }

  try {
    const { value: content } = await ElMessageBox.prompt('请输入记忆内容', '添加记忆', {
      confirmButtonText: '确认',
      cancelButtonText: '取消',
      inputPlaceholder: '请输入记忆内容'
    });

    if (!content || !content.trim()) {
      ElMessage.warning('记忆内容不能为空。');
      return;
    }

    const newMemory: Memory = {
      id: `memory_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`,
      content: content.trim()
    };

    // 更新本地数据
    memories.value.unshift(newMemory);

    // 保存到后端
    try {
      await axios.post('/userapi/updateMemory/', {
        "userid": userid,
        "update_data": memories.value
      });
      ElMessage.success('记忆添加成功！');
    } catch (error) {
      console.error('保存记忆失败:', error);
      ElMessage.error('记忆保存失败，请稍后再试。');
      // 如果保存失败，撤销添加
      memories.value.shift();
    }
  } catch (e) {
    // 用户取消操作
    if (e !== 'cancel') {
      console.error('添加记忆时发生错误:', e);
      ElMessage.error('添加记忆失败: ' + e);
    }
  }
};

// 编辑记忆
const editMemory = async (id: string) => {
  if (!userid) {
    ElMessage.error('用户未登录。');
    return;
  }

  const memory = memories.value.find(m => m.id === id);
  if (!memory) {
    ElMessage.error('未找到要编辑的记忆。');
    return;
  }

  try {
    const { value: newContent } = await ElMessageBox.prompt('编辑记忆内容', '编辑记忆', {
      confirmButtonText: '确认',
      cancelButtonText: '取消',
      inputValue: memory.content,
      inputPlaceholder: '请输入记忆内容'
    });

    if (!newContent || !newContent.trim()) {
      ElMessage.warning('记忆内容不能为空。');
      return;
    }

    // 更新本地数据
    const index = memories.value.findIndex(m => m.id === id);
    if (index !== -1) {
      const oldMemory = memories.value[index];
      memories.value[index] = {
        ...memory,
        content: newContent.trim()
      };

      // 保存到后端
      try {
        await axios.post('/userapi/updateMemory/', {
          "userid": userid,
          "update_data": memories.value
        });
        ElMessage.success('记忆更新成功！');
      } catch (error) {
        console.error('保存记忆失败:', error);
        ElMessage.error('记忆保存失败，请稍后再试。');
        // 如果保存失败，恢复原数据
        memories.value[index] = oldMemory;
      }
    }
  } catch (e) {
    // 用户取消操作
    if (e !== 'cancel') {
      console.error('编辑记忆时发生错误:', e);
      ElMessage.error('编辑记忆失败: ' + e);
    }
  }
};

// 删除记忆
const deleteMemory = async (id: string) => {
  if (!userid) {
    ElMessage.error('用户未登录。');
    return;
  }

  try {
    await ElMessageBox.confirm('确定要删除这条记忆吗？此操作不可逆。', '删除确认', {
      confirmButtonText: '确认删除',
      cancelButtonText: '取消',
      type: 'warning'
    });

    const initialLength = memories.value.length;
    const deletedMemory = memories.value.find(m => m.id === id);
    memories.value = memories.value.filter(memory => memory.id !== id);

    if (memories.value.length < initialLength) {
      try {
        await axios.post('/userapi/updateMemory/', {
          "userid": userid,
          "update_data": memories.value
        });
        ElMessage.success('记忆删除成功！');
      } catch (error) {
        console.error('保存记忆失败:', error);
        ElMessage.error('记忆保存失败，请稍后再试。');
        // 如果保存失败，恢复删除的记忆
        if (deletedMemory) {
          memories.value.push(deletedMemory);
        }
      }
    }
  } catch (e) {
    // 用户取消删除操作
    if (e !== 'cancel') {
      console.error('删除记忆时发生错误:', e);
      ElMessage.error('删除记忆失败: ' + e);
    }
  }
};

// 加载记忆数据
const loadMemories = async () => {
  if (!userid) {
    console.error("User not logged in");
    return;
  }

  try {
    const response = await axios.get('/userapi/getMemory/', {
      params: { userid: userid }
    });

    if (response.data.status === 'success' && Array.isArray(response.data.memory)) {
      memories.value = response.data.memory.map((item: any) => ({
        id: item.id || `memory_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`,
        content: item.content || ''
      }));
    } else {
      memories.value = [];
    }
  } catch (error) {
    console.error('加载记忆失败:', error);
    ElMessage.error('加载记忆失败，请稍后再试。');
    memories.value = [];
  }
};

onMounted(() => {
  if (userid) {
    // 加载个人信息
    axios.get('/userapi/getSelfInfo/', {
      params: { userid: userid }
    }).then(response => {
      if (response.data.status === 'success') {
        userInfo.value = response.data.info || { id: userid };
      } else {
        userInfo.value = { id: userid };
      }
    }).catch(error => {
      console.error('获取用户信息失败:', error);
      userInfo.value = { id: userid };
    });

    // 加载健康记录
    axios.get('/userapi/getHealthInfo/', {
      params: { userid: userid }
    }).then(response => {
      if (response.data.status === 'success' && Array.isArray(response.data.info)) {
        healthRecords.value = response.data.info.map((record: any, index: number) => ({
          id: record.id || `client_${record.date || Date.now()}_${index}`,
          description: record.description || '无描述',
          date: record.date || Date.now(),
          tags: record.tags || []
        }));
        healthRecords.value.sort((a, b) => b.date - a.date);
      } else {
        healthRecords.value = [];
      }
    }).catch(error => {
      console.error('获取健康记录失败:', error);
      healthRecords.value = [];
    });

    loadMemories();
  } else {
    console.error("User not logged in!");
    ElMessage.warning('请先登录。');
  }
})
</script>

<style scoped>
.self-container {
  display: flex;
  height: 100%;
  gap: 15px;
}

.glass-card {
  background: var(--bg-color-glass);
  border-radius: var(--border-radius);
  backdrop-filter: blur(15px);
  -webkit-backdrop-filter: blur(15px);
  border: var(--glass-border);
  box-shadow: var(--box-shadow);
  transition: all var(--transition-speed) ease;
}

.glass-card:hover {
  box-shadow: var(--box-shadow-hover);
}

/* 左侧个人信息 */
.profile-container {
  width: 28%;
  padding: 20px;
  display: flex;
  flex-direction: column;
  overflow: auto;
}

.profile-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 20px;
}

.user-name {
  margin: 0 0 5px 0;
  font-size: 1.5em;
  color: var(--text-color-primary);
}

.user-id {
  color: var(--text-color-secondary);
  font-size: 0.9em;
  margin-bottom: 5px;
}

.profile-info {
  margin-bottom: 20px;
}

.info-item {
  display: flex;
  margin-bottom: 12px;
  align-items: center;
}

.info-label {
  flex: 0 0 30%;
  color: var(--text-color-secondary);
  font-size: 0.9em;
}

.info-value {
  flex: 1;
  color: var(--text-color-primary);
}

.edit-profile {
  margin-top: auto;
  display: flex;
  justify-content: center;
}

/* 右侧面板 */
.right-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  border-bottom: 1px solid var(--border-color);
}

.section-header h3 {
  margin: 0;
  font-weight: 500;
  color: var(--text-color-primary);
}

/* 健康记录时间线 */
.health-timeline {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.no-records-message {
  padding: 20px;
  text-align: center;
  color: var(--text-color-secondary);
  font-style: italic;
}

.section-header .edit-actions {
  display: flex;
  gap: 10px;
}

.timeline-card {
  background: rgba(255, 255, 255, 0.6);
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 10px;
  transition: all var(--transition-speed) ease;
  position: relative;
}

.timeline-card:hover {
  background: rgba(255, 255, 255, 0.8);
  transform: translateY(-2px);
}

.record-description {
  margin: 0 0 12px 0;
  color: var(--text-color-primary); /* Making description more prominent */
  font-size: 1em; /* Slightly larger */
  line-height: 1.5;
}

.record-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
  margin-bottom: 8px;
}

.record-actions {
  position: absolute;
  right: 10px;
  top: 10px;
  display: flex;
  gap: 5px;
  opacity: 0;
  transition: opacity var(--transition-speed) ease;
}

.timeline-card:hover .record-actions {
  opacity: 1;
}

/* 记忆管理 */
.memory-container {
  height: 300px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.memory-list {
  padding: 15px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.memory-card {
  background: rgba(255, 255, 255, 0.6);
  border-radius: 8px;
  padding: 15px;
  position: relative;
  transition: all var(--transition-speed) ease;
  display: flex;
  align-items: center;
}

.memory-card:hover {
  background: rgba(255, 255, 255, 0.8);
  transform: translateX(3px);
}

.memory-content {
  flex: 1;
  line-height: 1.5;
}

.memory-actions {
  display: flex;
  gap: 5px;
  opacity: 0;
  transition: opacity var(--transition-speed) ease;
}

.memory-card:hover .memory-actions {
  opacity: 1;
}

/* 滚动条样式 */
:deep(.el-scrollbar__bar) {
  opacity: 0.2;
}

:deep(.el-scrollbar__bar:hover) {
  opacity: 0.4;
}

/* Timeline 样式定制 */
:deep(.el-timeline-item__node) {
  z-index: 1;
}

:deep(.el-timeline-item__wrapper) {
  padding-left: 20px;
}

:deep(.el-timeline-item__tail) {
  border-left: 2px solid var(--border-color);
}

:deep(.el-divider__text) {
  background-color: transparent;
  color: var(--primary-color);
  font-weight: 500;
}
</style> 