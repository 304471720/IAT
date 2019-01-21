import React, { PureComponent } from 'react';
import {
  List, Tree ,Select,Icon,Menu,message,Input,Card,Divider,TimePicker,Button,Switch,Spin
} from 'antd';
import {connect} from 'dva';
import moment from 'moment';

import PageHeaderWrapper from '@/components/PageHeaderWrapper'
import styles from './index.less'

const { Option } = Select;

@connect(({ system,task,loading }) => ({
  system,
  task,
  loading:loading.effects["task/queryTaskList"]
}))
class Timing extends PureComponent {
  state={
    taskList:[],
  };

  componentWillMount() {
    this.queryTaskList()
  }

  queryTaskList=()=>{
    const {dispatch} = this.props;
    dispatch({
      type:'task/queryTaskList',
      payload:{
        taskType: 2,
      }
    })
      .then(()=>{
        const {task} = this.props;
        this.setState({taskList:task.taskList})
      })
  };

  handleAddTask=()=>{
    const {dispatch} = this.props;
    dispatch({
      type:'task/goTimAddPage'
    })
  };

  handleStateChange=(checked,id)=>{
    if (checked){
      this.handleRunTask(id)
    }else {
      this.querySetTaskStatus(id,4)
    }
  };

  handleRunTask=(id)=>{
    const {dispatch} = this.props;
    dispatch({
      type:'task/queryTaskExcute',
      payload:{
        id,
      }
    })
      .then(()=>{
        this.queryTaskList()
      })

  };

  handleTimeChange=(id,e)=>{
    const runTime = moment(e).format('HH:mm')
    const {dispatch} = this.props;
    dispatch({
      type:'task/queryUpdateRunTime',
      payload:{
        id,
        runTime,
      }
    })
      .then(()=>{
        this.queryTaskList()
      })
  }

  querySetTaskStatus=(id,status)=>{
    const {dispatch} = this.props;
    dispatch({
      type:'task/querySetTaskStatus',
      payload:{
        id,
        status,
      }
    })
      .then(()=>{
        this.queryTaskList()
      })
  }

  render() {
    const {loading} = this.props;
    const content = (
      <div className={styles.pageHeaderContent}>
        <p>
          功能简介：每日任务定时执行， 并邮件通知，若要修改请先关闭任务。
        </p>
      </div>
    );
    const description = item => (
      <div className={styles.descriptionContainer}>
        <div className={styles.item_container}>
          <span>执行时间：</span>
          <TimePicker
            format='HH:mm'
            size="small"
            value={moment(item.runTime, 'HH:mm')}
            style={{
              margin: '8px 0',
            }}
            onChange={(e)=>this.handleTimeChange(item.id,e)}
          />
        </div>
        <div className={styles.item_container}>
          <span>任务描述：</span>
          <div>{item.taskDesc}</div>
        </div>
        {item.status===3&&(
          <div className={styles.reportHref}>
            <a style={{color:'#40a9ff',fontWeight:'bold'}} href={`#/task/timing/report?${item.id}`}>查看报告 <Icon type="right" /></a>
          </div>
        )}
      </div>
    );
    const cardTitle = item => {
      return (
        <div className={styles.switchContainer}>
          <a href={`#/task/timing/detail?${item.id}`} style={{color:'#40a9ff',fontWeight:'bold'}}>
            {item.name}
          </a>
          <div className={styles.switchButton}>
            <Switch
              checkedChildren="开"
              unCheckedChildren="关"
              checked={!(item.status === 0 ||item.status === 4 )}
              onChange={checked => this.handleStateChange(checked, item.id)}
            />
          </div>
        </div>
      );
    };
    return (
      <PageHeaderWrapper title="每日任务列表" content={content}>
        <div className={styles.cardList}>
          <List
            loading={loading}
            rowKey="id"
            grid={{ gutter: 24, lg: 3, md: 2, sm: 1, xs: 1 }}
            dataSource={[...this.state.taskList, '']}
            renderItem={item =>
              item ? (
                <List.Item key={item.id}>
                  <Card
                    hoverable
                    className={styles.card}
                    // actions={[<Icon style={{color:'red'}} type="delete" />]}
                  >
                    <Card.Meta title={cardTitle(item)} description={description(item)} />
                  </Card>
                </List.Item>
              ) : (
                <List.Item>
                  <Button
                    type="dashed"
                    className={styles.newButton}
                    onClick={() => this.handleAddTask()}
                  >
                    <Icon type="plus" /> 新增任务
                  </Button>
                </List.Item>
              )
            }
          />
        </div>
      </PageHeaderWrapper>
    );
  }
}
export default Timing
