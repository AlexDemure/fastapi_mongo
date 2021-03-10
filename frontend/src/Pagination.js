import React, {Component} from 'react';

class Pagination extends Component {
  constructor(props) {
    super(props);
    this.state = {
      items: []
    };
  }

  createItems = () => {
    let {count_pages, current_page} = this.props;
    let items = [];
    let filling = (start, end) => {
      let arr = [];
      for(let i = start; i < end; i++) {
        arr.push(i+1);
      }
      return arr;
    }

    if(count_pages < 8) {
      items = filling(0, count_pages);
    } else {
      if(current_page < 5) {
        items = [...filling(0, 5), '...', count_pages];
      } else if(current_page > count_pages-4) {
        items = [1, '...', ...filling(count_pages-5, count_pages)];
      } else {
        items = [1, '...', current_page-1, current_page, current_page+1, '...', count_pages];
      }
    }
    this.setState({
      items
    });
  }

  nextPage = () => {
    const {current_page, onChangePage, count_pages} = this.props;
    if(current_page < count_pages) {
      onChangePage(current_page+1);
    }
  }

  prevPage = () => {
    const {current_page, onChangePage} = this.props;
    if(current_page > 1) {
      onChangePage(current_page-1);
    }
  }

  componentDidUpdate(prevProps) {
    if(prevProps.current_page !== this.props.current_page ||
       prevProps.count_pages !== this.props.count_pages) {
      this.createItems();
    }
  }

  componentDidMount() {
    this.createItems();
  }

  render() {
    let {items} = this.state;
    const {current_page, onChangePage} = this.props;
    return(
      <div className='pagination' style={{'gridTemplateColumns': `repeat(${items.length+2}, 40px)`}}>
        <div className='prev_arrow' onClick={this.prevPage}/>
        {
          items.map((item, i) => (
            item === '...' ?
              <div key={i} className='dots'>{item}</div>
              :
              <div key={i} className={current_page === item ? 'current' : 'page'} onClick={() => {onChangePage(item)}}>{item}</div>
          ))
        }
        <div className='next_arrow' onClick={this.nextPage}/>
      </div>
    )
  }
}

export default Pagination;