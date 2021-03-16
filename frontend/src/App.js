import React, {Component} from 'react';
import moment from 'moment';
import Chart from "chart.js";
import axios from 'axios';
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";
import ru from 'date-fns/locale/ru';
import Pagination from './Pagination';
import Select from './Select';
import './App.css';

class App extends Component {
  constructor(props) {
    super(props);
    this.state = {
      points: [],
      startDate: moment().set({'year': 2020, 'month': 5, 'date': 1}),
      endDate: moment(),
      show_calendar: false,
      selected_date: 'all', //all, last, 21.02.2021-23.02.2021
      total_hours_listened: 0,
      hours_listened_in_week: 0,
      total_listeners: 0,
      listeners_in_week: 0,
      average_listening_percentage: 0,
      average_listening_in_week: 0,
      count_pages: 1,
      current_page: 1,
      limit: 10,
      episodes: [],
      count_rows: 0,
      total_rows: 0
    };
  }

  onToggleCalendar = () => {
    this.setState({
      show_calendar: !this.state.show_calendar
    });
  }

  onChangeSelectedDate = (value) => {
    let startDate = null;
    let endDate = null;
    if(value === 'all') {
      startDate = moment().set({'year': 2020, 'month': 5, 'date': 1});
      endDate = moment();
    }
    if(value === 'last') {
      startDate = moment().subtract(1, 'months');
      endDate = moment();
    }

    this.setState({
      selected_date: value,
      startDate: Date.parse(startDate),
      endDate: Date.parse(endDate)
    }, () => {this.getEpisodesData(); this.getDiagramData()});
  }

  onChangeDate = (dates) => {
    const [start, end] = dates;
    let selected_date = `${moment(start).format('DD.MM.YYYY')}-${moment(end).format('DD.MM.YYYY')}`;
    this.setState({
      startDate: start,
      endDate: end,
      selected_date: selected_date
    }, () => {this.getEpisodesData(); this.getDiagramData()});
  }

  onChangeLimit = (limit) => {
    this.setState({
      limit,
      current_page: 1
    }, this.getEpisodesData);
  }

  onChangePage = (page) => {
    this.setState({
      current_page: page
    }, this.getEpisodesData);
  }

  getTotalData = () => {
    let request = {
      books: [
        "0405010081641",
        "0405010087919",
        "0405010083614",
        "0405010083416",
        "0405010083348",
        "0405010075442"
      ]
    };
    axios.post('http://localhost:7040/api/v1/statistics/total/', request).then(res => {
      this.setState({
        total_hours_listened: Math.floor(res.data.total_hours_listened),
        hours_listened_in_week: Math.floor(res.data.hours_listened_in_week),
        total_listeners: res.data.total_listeners,
        listeners_in_week: res.data.listeners_in_week,
        average_listening_percentage: Math.floor(res.data.average_listening_percentage),
        average_listening_in_week: Math.floor(res.data.average_listening_in_week)
      });
    });
  }

  getDiagramXlsx = () => {
    let {limit, current_page, startDate, endDate} = this.state;
    let request = {
      books: [
        "0405010081641",
        "0405010087919",
        "0405010083614",
        "0405010083416",
        "0405010083348",
        "0405010075442"
      ],
      start_date: startDate,
      end_date: endDate,
      limit: limit,
      offset: (current_page-1) * limit  //'-1' потому что отчет с первой страницы, а не с нулевой. при умножении отбрасывается корректное количество записей таблицы на предыдущих страницах
    };
    axios.post('http://localhost:7040/api/v1/statistics/analytics/xlsx/', request).then(res => {
      console.log(res.data);
    });
  }

  getEpisodesXlsx = () => {
    let {limit, current_page, startDate, endDate} = this.state;
    let request = {
      books: [
        "0405010081641",
        "0405010087919",
        "0405010083614",
        "0405010083416",
        "0405010083348",
        "0405010075442"
      ],
      start_date: startDate,
      end_date: endDate,
      limit: limit,
      offset: (current_page-1) * limit  //'-1' потому что отчет с первой страницы, а не с нулевой. при умножении отбрасывается корректное количество записей таблицы на предыдущих страницах
    };
    axios.post('http://localhost:7040/api/v1/statistics/episodes/xlsx/', request).then(res => {
      console.log(res.data);
    });
  }

  getDiagramData = () => {
    let {startDate, endDate} = this.state;
    let request = {
      books: [
        "0405010081641",
        "0405010087919",
        "0405010083614",
        "0405010083416",
        "0405010083348",
        "0405010075442"
      ],
      start_date: startDate,
      end_date: endDate
    };
    axios.post('http://localhost:7040/api/v1/statistics/diagram/', request).then(res => {
      this.setState({
        points: res.data.points
      }, this.createDiagram);
    });
  }

  createDiagram = () => {
    let {points} = this.state;
    let ctx = this.canvas.getContext('2d');
    new Chart(ctx, {
      type: 'line',
      data: {
        labels: points.map(item => (moment(item.day).format('MM.DD'))),
        datasets: [{
          data: points.map(item => (item.total_hours)),
          backgroundColor: points.map(item => ('#FF5C28')),
          borderWidth: 3,
          borderColor: 'rgba(255, 92, 40, 1)',
          fill: false
        }]
      },
      options: {
        legend: {
          display: false
        },
        scales: {
          yAxes: [{
            ticks: {
              beginAtZero: true
            }
          }]
        }
      }
    });
  }

  getEpisodesData = () => {
    let {limit, current_page, startDate, endDate} = this.state;
    let request = {
      books: [
        "0405010081641",
        "0405010087919",
        "0405010083614",
        "0405010083416",
        "0405010083348",
        "0405010075442"
      ],
      start_date: startDate,
      end_date: endDate,
      limit: limit,
      offset: (current_page-1) * limit  //'-1' потому что отчет с первой страницы, а не с нулевой. при умножении отбрасывается корректное количество записей таблицы на предыдущих страницах
    };
    axios.post('http://localhost:7040/api/v1/statistics/episodes/', request).then(res => {
      this.setState({
        count_pages: res.data.count_pages,
        episodes: res.data.rows,
        count_rows: res.data.count_rows,
        total_rows: res.data.total_rows
      });
    });
  }

  componentDidMount() {
    this.getTotalData();
    this.getDiagramData();
    this.getEpisodesData();
  }

  render() {
    let {
      startDate,
      endDate,
      show_calendar,
      selected_date,
      total_hours_listened,
      hours_listened_in_week,
      total_listeners,
      listeners_in_week,
      average_listening_percentage,
      average_listening_in_week,
      count_pages,
      current_page,
      limit,
      episodes,
      count_rows,
      total_rows
    } = this.state;

    let options = [
      {
        name: '10',
        value: 10,
        selected: limit === 10
      },
      {
        name: '20',
        value: 20,
        selected: limit === 20
      }
    ];

    return (
      <div className="App">
        <div className="top">
          <h1>Статистика прослушиваний</h1>
          <div className="date">
            <div className="selected_date" onClick={this.onToggleCalendar}>
              <span>
                {
                  selected_date === 'all' ? 'Весь период'
                    : selected_date === 'last' ? 'Последний месяц'
                    : selected_date
                }
              </span>
            </div>
            {
              show_calendar &&
              <div className="calendar">
                <DatePicker
                  selected={startDate}
                  onChange={this.onChangeDate}
                  startDate={startDate}
                  endDate={endDate}
                  locale={ru}
                  monthsShown={2}
                  selectsRange
                  inline
                />
                <span className={`btn ${selected_date === 'all' ? 'active' : ''}`} onClick={() => {this.onChangeSelectedDate('all')}}>Весь период</span>
                <span className={`btn ${selected_date === 'last' ? 'active' : ''}`} onClick={() => {this.onChangeSelectedDate('last')}}>Последний месяц</span>
              </div>
            }
          </div>
        </div>
        <div className="total">
          <div className="item">
            <p className="week">+{hours_listened_in_week}ч. за нед.</p>
            <p className="count">{total_hours_listened}</p>
            <p className="name">ВСЕГО ПРОСЛУШАННЫХ ЧАСОВ</p>
          </div>
          <div className="item">
            <p className="week">+{listeners_in_week} чел. за нед.</p>
            <p className="count">{total_listeners} <span>чел.</span></p>
            <p className="name">ВСЕГО СЛУШАТЕЛЕЙ</p>
          </div>
          <div className="item">
            <p className="week">{average_listening_in_week}% за нед.</p>
            <p className="count">{average_listening_percentage}%</p>
            <p className="name">СРЕДНИЙ % ДОСЛУШИВАНИЙ</p>
          </div>
        </div>
        <div className="title">
          <h1>Всего прослушанных часов</h1>
          <span onClick={this.getDiagramXlsx}>Скачать .xlsx</span>
        </div>
        <canvas className="diagram" ref={node => this.canvas = node} height={500}/>
        <div className="title">
          <h1>Прослушивания по эпизодам</h1>
          <span onClick={this.getEpisodesXlsx}>Скачать .xlsx</span>
        </div>
        <div className="table">
          <div className="table-header">
            <div>ISBN</div>
            <div>НАЗВАНИЕ</div>
            <div>ДЛИТЕЛЬНОСТЬ</div>
            <div>ФОРМАТ</div>
            <div>ИМПРИНТ</div>
            <div>АВТОР</div>
            <div>ЧТЕЦ</div>
          </div>
          <div className="table-body">
            {
              episodes.map((item, i) => (
                <div className="table-body-row" key={i}>
                  <div>{item.isbn}</div>
                  <div>{item.name}</div>
                  <div>{item.duration}</div>
                  <div>{item.format}</div>
                  <div>{item.imprint}</div>
                  <div>{item.author}</div>
                  <div>{item.narrator}</div>
                </div>
              ))
            }
          </div>
        </div>
        <div className="control_table">
          <div className="count_rows">
            <Select
              onChange={(value) => {this.onChangeLimit(value)}}
              options={options}
            />
            <span className='total_rows'>
              Показано {count_rows} из {total_rows}
            </span>
          </div>
          <Pagination count_pages={count_pages}
                      current_page={current_page}
                      onChangePage={this.onChangePage}
          />
        </div>
        {/*<div className="title">*/}
        {/*  <h1>Название таблицы</h1>*/}
        {/*  <span>Скачать .xlsx</span>*/}
        {/*</div>*/}
        {/*<div className="table">*/}
        {/*  <div className="table-header">*/}
        {/*    <div>ISBN</div>*/}
        {/*    <div>НАЗВАНИЕ</div>*/}
        {/*    <div>ДЛИТЕЛЬНОСТЬ</div>*/}
        {/*    <div>ФОРМАТ</div>*/}
        {/*    <div>ИМПРИНТ</div>*/}
        {/*    <div>АВТОР</div>*/}
        {/*    <div>ЧТЕЦ</div>*/}
        {/*  </div>*/}
        {/*  <div className="table-body">*/}
        {/*    <div className="table-body-row">*/}
        {/*      <div>978-5-699-12014-7</div>*/}
        {/*      <div>Лечение Джорджа Марвелуса</div>*/}
        {/*      <div>11:39:46</div>*/}
        {/*      <div>abook</div>*/}
        {/*      <div>Импринт</div>*/}
        {/*      <div>Панов Емельян</div>*/}
        {/*      <div>Милюкова Ариадна</div>*/}
        {/*    </div>*/}
        {/*    <div className="table-body-row">*/}
        {/*      <div>978-5-699-12014-7</div>*/}
        {/*      <div>Лечение Джорджа Марвелуса</div>*/}
        {/*      <div>11:39:46</div>*/}
        {/*      <div>abook</div>*/}
        {/*      <div>Импринт</div>*/}
        {/*      <div>Панов Емельян</div>*/}
        {/*      <div>Милюкова Ариадна</div>*/}
        {/*    </div>*/}
        {/*    <div className="table-body-row">*/}
        {/*      <div>978-5-699-12014-7</div>*/}
        {/*      <div>Лечение Джорджа Марвелуса</div>*/}
        {/*      <div>11:39:46</div>*/}
        {/*      <div>abook</div>*/}
        {/*      <div>Импринт</div>*/}
        {/*      <div>Панов Емельян</div>*/}
        {/*      <div>Милюкова Ариадна</div>*/}
        {/*    </div>*/}
        {/*  </div>*/}
        {/*</div>*/}
        {/*<div className="control_table">*/}
        {/*  <div className="count_rows">*/}
        {/*    <Select*/}
        {/*      onChange={(value) => {this.onChangeLimit(value)}}*/}
        {/*      options={options}*/}
        {/*    />*/}
        {/*    <span className='total_rows'>*/}
        {/*      Показано 10 из 3 829*/}
        {/*    </span>*/}
        {/*  </div>*/}
        {/*  <Pagination count_pages={count_pages}*/}
        {/*              current_page={current_page}*/}
        {/*              onChangePage={this.onChangePage}*/}
        {/*  />*/}
        {/*</div>*/}
      </div>
    )
  }
}

export default App;