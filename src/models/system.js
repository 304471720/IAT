import {
  queryProjectList,
  queryAddProject,
  queryAddGlobalValues,
  queryDeleteGlobalValues,
  queryProjectGlobalValues,
  queryUpdateGlobalValues,
  queryAddProxyConfig,
  queryProxyConfigList,
  queryDeleteProxyConfig,
  querySetProjectStatus,
  queryGetAllLibs,
  queryGetLibKeywords,
  queryUpdateKeywords,
} from '@/services/api';

const SytemModel = {
  namespace: 'system',
  state: {
    projectList: [],
    proxyConfigList: [],
    globalValues: [],
    allLibs: [],
    libKeywords: [],
  },
  effects: {
    *queryProjectList({ payload }, { call, put }) {
      yield put({ type: 'updateState', payload: { projectList: [] } });
      const response = yield call(queryProjectList, payload);
      if (response) {
        yield put({ type: 'updateState', payload: { projectList: response.content } });
      }
    },
    *queryProjectGlobalValues({ payload }, { call, put }) {
      yield put({ type: 'updateState', payload: { globalValues: [] } });
      const response = yield call(queryProjectGlobalValues, payload);
      if (response) {
        yield put({ type: 'updateState', payload: { globalValues: response.content } });
      }
    },
    *queryProxyConfigList({ payload }, { call, put }) {
      yield put({ type: 'updateState', payload: { proxyConfigList: [] } });
      const response = yield call(queryProxyConfigList, payload);
      if (response) {
        yield put({ type: 'updateState', payload: { proxyConfigList: response.content } });
      }
    },
    *queryGetAllLibs({ payload }, { call, put }) {
      yield put({ type: 'updateState', payload: { allLibs: [] } });
      const response = yield call(queryGetAllLibs, payload);
      if (response) {
        yield put({ type: 'updateState', payload: { allLibs: response.content } });
      }
    },
    *queryGetLibKeywords({ payload }, { call, put }) {
      yield put({ type: 'updateState', payload: { libKeywords: [] } });
      const response = yield call(queryGetLibKeywords, payload);
      if (response) {
        yield put({ type: 'updateState', payload: { libKeywords: response.content } });
      }
    },
    *queryAddProject({ payload }, { call, put }) {
      yield call(queryAddProject, payload);
    },
    *queryUpdateKeywords({ payload }, { call, put }) {
      yield call(queryUpdateKeywords, payload);
    },
    *queryDeleteProxyConfig({ payload }, { call, put }) {
      yield call(queryDeleteProxyConfig, payload);
    },
    *querySetProjectStatus({ payload }, { call, put }) {
      yield call(querySetProjectStatus, payload);
    },
    *queryAddProxyConfig({ payload }, { call, put }) {
      yield call(queryAddProxyConfig, payload);
    },
    *queryUpdateGlobalValues({ payload }, { call, put }) {
      yield call(queryUpdateGlobalValues, payload);
    },
    *queryAddGlobalValues({ payload }, { call, put }) {
      yield call(queryAddGlobalValues, payload);
    },
    *queryDeleteGlobalValues({ payload }, { call, put }) {
      yield call(queryDeleteGlobalValues, payload);
    },
  },
  reducers: {
    updateState(state, { payload }) {
      return { ...state, ...payload };
    },
  },
};
export default SytemModel;
